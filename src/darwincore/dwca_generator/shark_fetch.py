import csv
import fnmatch
import io
import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import NamedTuple

import click
import requests

from darwincore import TMP_DATASETS_DIR
from darwincore.errors import ConfigurationError, DarwinCoreError, SharkFetchError

SHARK_API_URL = "https://shark.smhi.se/api"
OLD_DATASETS_DIR_NAME = "old_datasets"

logger = logging.getLogger("dwca_generator")


@dataclass(frozen=True)
class FetchOptions:
    from_date: date | None = None
    to_date: date | None = None

    def __post_init__(self):
        if all((self.from_date, self.to_date)) and self.from_date > self.to_date:
            raise DarwinCoreError("FetchOptions from_date can't be after to_date")


class SharkDataset(NamedTuple):
    name: str
    datatype: str
    version: str
    file_name: str


def parse_dataset_list(table_text: str) -> list[SharkDataset]:
    """Parse the dataset table returned by the SHARK API."""
    reader = csv.DictReader(io.StringIO(table_text), delimiter="\t")
    return [
        SharkDataset(
            name=row["Dataset name"],
            datatype=row["Datatype"],
            version=row["Version"],
            file_name=row["Dataset file name"],
        )
        for row in reader
        if row.get("Dataset file name")
    ]


class SharkApiClient:
    """Client for the SHARK API. Reuses one connection for all requests."""

    def __init__(
        self, base_url: str = SHARK_API_URL, session: requests.Session | None = None
    ):
        self._base_url = base_url
        logger.debug("Creating SHARK API client")
        self._session = session or requests.Session()

    def close(self):
        self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        logger.debug("Closing SHARK API client")
        self.close()

    def list_datasets(
        self, from_date: date | None, to_date: date | None, datatype: str
    ) -> list[SharkDataset]:
        """List SHARK datasets of a datatype with a version date within the given span."""
        response = self._session.get(
            f"{self._base_url}/dataset/table.txt",
            params={
                "from_date": from_date.isoformat() if from_date else None,
                "to_date": to_date.isoformat() if to_date else None,
                "datatype": datatype,
            },
            headers={"accept": "text/plain"},
            timeout=60,
        )
        response.raise_for_status()
        response.encoding = "utf-8"
        return parse_dataset_list(response.text)

    def download_dataset(self, file_name: str, target_dir: Path) -> Path:
        """Download a SHARK dataset zip file unless it already exists in target_dir."""
        target_path = target_dir / file_name
        if target_path.exists():
            logger.debug("SHARK dataset already exists: %s", file_name)
            return target_path

        target_dir.mkdir(parents=True, exist_ok=True)
        part_path = target_dir / (file_name + ".part")
        logger.debug("Downloading SHARK dataset: %s", file_name)
        with self._session.get(
            f"{self._base_url}/dataset/download/{file_name}",
            headers={"accept": "application/octet-stream"},
            stream=True,
            timeout=60,
        ) as response:
            response.raise_for_status()
            with open(part_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    file.write(chunk)
        part_path.replace(target_path)
        return target_path


def fetch_source_files(
    fetch_options: FetchOptions, source_files_config: dict
) -> list[str]:
    """Download the SHARK datasets configured in sourceFiles and return their paths."""
    data_type = source_files_config.get("sharkDatatype", "")
    glob_pattern = source_files_config.get("globSearch", "")

    if not data_type:
        logger.info("No SHARK datatype configured, nothing to download.")
        return []
    if not glob_pattern:
        raise ConfigurationError("Missing glob pattern needed to download source files.")

    remove_partial_downloads(TMP_DATASETS_DIR)

    try:
        with SharkApiClient() as api_client:
            data_listing = api_client.list_datasets(
                fetch_options.from_date, fetch_options.to_date, data_type
            )
            latest_datasets = filter_datasets(data_listing, glob_pattern)
            datasets_to_process = {dataset.file_name for dataset in latest_datasets}
            local_datasets = find_local_datasets(datasets_to_process, TMP_DATASETS_DIR)
            files_to_download = datasets_to_process - local_datasets
            logger.info(
                "Found %s matching SHARK datasets. %s already on disk, %s to download.",
                len(datasets_to_process),
                len(local_datasets),
                len(files_to_download),
            )
            if files_to_download and not click.confirm(
                f"Download {len(files_to_download)} SHARK datasets?", default=True
            ):
                logger.info("Download of SHARK datasets cancelled.")
                return []
            downloaded_files = [str(TMP_DATASETS_DIR / name) for name in local_datasets]
            if files_to_download:
                with click.progressbar(
                    sorted(files_to_download),
                    label="Downloading SHARK datasets",
                    item_show_func=lambda name: name,
                ) as file_names:
                    for file_name in file_names:
                        path = api_client.download_dataset(file_name, TMP_DATASETS_DIR)
                        downloaded_files.append(str(path))
    except requests.RequestException as e:
        raise SharkFetchError(f"Failed to fetch SHARK datasets: {e}") from e

    move_outdated_datasets(latest_datasets, TMP_DATASETS_DIR)
    return sorted(downloaded_files)


def filter_datasets(datasets: list[SharkDataset], glob_pattern: str) -> set[SharkDataset]:
    # Glob matching differs by platform, making lower case to get the same behavior.
    lowercase_glob_pattern = glob_pattern.lower()
    matching_datasets = {
        dataset
        for dataset in datasets
        if fnmatch.fnmatch(dataset.file_name.lower(), lowercase_glob_pattern)
    }

    by_name: dict[str, list[SharkDataset]] = {}
    for dataset in matching_datasets:
        by_name.setdefault(dataset.name, []).append(dataset)

    return {
        max(versions, key=lambda dataset: dataset.version)
        for versions in by_name.values()
    }


def move_outdated_datasets(datasets: Iterable[SharkDataset], directory: Path) -> None:
    """Move older local versions of the given datasets to directory/old_datasets."""
    old_datasets_dir = directory / OLD_DATASETS_DIR_NAME
    for dataset in datasets:
        pattern = re.compile(
            re.escape(dataset.name) + r"_version_(\d{4}-\d{2}-\d{2})\.zip"
        )
        for path in directory.iterdir():
            match = pattern.fullmatch(path.name)
            if match and path.is_file() and match.group(1) < dataset.version:
                old_datasets_dir.mkdir(exist_ok=True)
                logger.info("Moving outdated SHARK dataset: %s", path.name)
                path.replace(old_datasets_dir / path.name)


def find_local_datasets(file_names: set[str], directory: Path) -> set[str]:
    """Return the file names that are already present in local directory."""
    return {name for name in file_names if (directory / name).exists()}


def remove_partial_downloads(directory: Path) -> None:
    """Remove .part files left behind by interrupted downloads."""
    for path in directory.glob("*.part"):
        logger.debug("Removing partial SHARK download: %s", path.name)
        try:
            path.unlink()
        except OSError as e:
            logger.warning("Failed to remove partial SHARK download %s: %s", path.name, e)
