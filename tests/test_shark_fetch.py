import pytest

from darwincore.dwca_generator.shark_fetch import (
    OLD_DATASETS_DIR_NAME,
    SharkDataset,
    filter_datasets,
    move_outdated_datasets,
    remove_partial_downloads,
)


@pytest.mark.parametrize(
    "given_datasets, given_glob_search, expected_datasets",
    (
        (
            [
                SharkDataset(
                    name="SHARK_Jellyfish_2007_2014_GU",
                    datatype="Jellyfish",
                    version="2023-04-27",
                    file_name="SHARK_Jellyfish_2007_2014_GU_version_2023-04-27.zip",
                ),
                SharkDataset(
                    name="SHARK_Picoplankton_1995_SMHI_IFCB",
                    datatype="Picoplankton",
                    version="2025-03-09",
                    file_name="SHARK_Picoplankton_1995_SMHI_IFCB_version_2025-03-09.zip",
                ),
                SharkDataset(
                    name="WHALE_Phytoplankton_2023_SMHI_IFCB",
                    datatype="Phytoplankton",
                    version="2026-10-13",
                    file_name="WHALE_Phytoplankton_2023_SMHI_IFCB_version_2026-10-13",
                ),
            ],
            "SHARK_Phytoplankton_*_version_*.zip",
            set(),
        ),  # No matching datasets
        (
            [
                SharkDataset(
                    name="SHARK_Jellyfish_2007_2014_GU",
                    datatype="Jellyfish",
                    version="2023-04-27",
                    file_name="SHARK_Jellyfish_2007_2014_GU_version_2023-04-27.zip",
                ),
                SharkDataset(
                    name="SHARK_Phytoplankton_1995_SMHI_IFCB",
                    datatype="Phytoplankton",
                    version="2025-03-09",
                    file_name="SHARK_Phytoplankton_1995_SMHI_IFCB_version_2025-03-09.zip",
                ),
                SharkDataset(
                    name="SHARK_Phytoplankton_2023_SMHI_IFCB",
                    datatype="Phytoplankton",
                    version="2026-10-13",
                    file_name="SHARK_Phytoplankton_2023_SMHI_IFCB_version_2026-10-13",
                ),
            ],
            "SHARK_Phytoplankton_*_version_*.zip",
            {"SHARK_Phytoplankton_1995_SMHI_IFCB_version_2025-03-09.zip"},
        ),  # Only one file matching pattern
        (
            [
                SharkDataset(
                    name="SHARK_Phytoplankton_1995_SMHI_IFCB",
                    datatype="Phytoplankton",
                    version="2023-04-27",
                    file_name="SHARK_Phytoplankton_1995_SMHI_IFCB_version_2023-04-27.zip",
                ),
                SharkDataset(
                    name="SHARK_Phytoplankton_2000_SMHI_IFCB",
                    datatype="Phytoplankton",
                    version="2025-03-09",
                    file_name="SHARK_Phytoplankton_2000_SMHI_IFCB_version_2025-03-09.zip",
                ),
                SharkDataset(
                    name="SHARK_Phytoplankton_2005_SMHI_IFCB",
                    datatype="Phytoplankton",
                    version="2026-10-13",
                    file_name="SHARK_Phytoplankton_2005_SMHI_IFCB_version_2026-10-13.zip",
                ),
            ],
            "SHARK_Phytoplankton_*_version_*.zip",
            {
                "SHARK_Phytoplankton_1995_SMHI_IFCB_version_2023-04-27.zip",
                "SHARK_Phytoplankton_2000_SMHI_IFCB_version_2025-03-09.zip",
                "SHARK_Phytoplankton_2005_SMHI_IFCB_version_2026-10-13.zip",
            },
        ),  # Multiple matching datasets
        (
            [
                SharkDataset(
                    name="sHaRk_PhYtOpLaNkToN_1995_2001_uMsC",
                    datatype="Phytoplankton",
                    version="2025-03-09",
                    file_name="sHaRk_PhYtOpLaNkToN_1995_2001_uMsC_vErSioN_2025-03-09.zip",
                ),
            ],
            "SHARK_Phytoplankton_*_version_*.zip",
            {"sHaRk_PhYtOpLaNkToN_1995_2001_uMsC_vErSioN_2025-03-09.zip"},
        ),  # Disregarding case in matching
        (
            [
                SharkDataset(
                    name="SHARK_Phytoplankton_1995_SMHI_IFCB",
                    datatype="Phytoplankton",
                    version="2024-01-01",
                    file_name="SHARK_Phytoplankton_1995_SMHI_IFCB_version_2024-01-01.zip",
                ),
                SharkDataset(
                    name="SHARK_Phytoplankton_1995_SMHI_IFCB",
                    datatype="Phytoplankton",
                    version="2026-10-13",
                    file_name="SHARK_Phytoplankton_1995_SMHI_IFCB_version_2026-10-13.zip",
                ),
                SharkDataset(
                    name="SHARK_Phytoplankton_1995_SMHI_IFCB",
                    datatype="Phytoplankton",
                    version="2025-12-31",
                    file_name="SHARK_Phytoplankton_1995_SMHI_IFCB_version_2025-12-31.zip",
                ),
            ],
            "SHARK_Phytoplankton_*_version_*.zip",
            {"SHARK_Phytoplankton_1995_SMHI_IFCB_version_2026-10-13.zip"},
        ),  # Multiple matching datasets, latest version is selected
    ),
)
def test_filter_datasets(given_datasets, given_glob_search, expected_datasets):
    # Given a list of datasets
    # Given a glob pattern
    # When filtering the datasets with the pattern
    filtered_datasets = filter_datasets(given_datasets, given_glob_search)

    # Then only the datasets with matching file names remain
    filtered_file_names = {dataset.file_name for dataset in filtered_datasets}
    assert filtered_file_names == expected_datasets


@pytest.mark.parametrize(
    "given_local_files, given_datasets, expected_remaining_files, expected_moved_files",
    (
        (
            [
                "SHARK_Phytoplankton_1995_SMHI_IFCB_version_2024-01-01.zip",
                "SHARK_Phytoplankton_1995_SMHI_IFCB_version_2025-03-09.zip",
                "SHARK_Phytoplankton_2000_SMHI_IFCB_version_2023-04-27.zip",
            ],
            [
                SharkDataset(
                    name="SHARK_Phytoplankton_1995_SMHI_IFCB",
                    datatype="Phytoplankton",
                    version="2025-03-09",
                    file_name="SHARK_Phytoplankton_1995_SMHI_IFCB_version_2025-03-09.zip",
                ),
            ],
            {
                "SHARK_Phytoplankton_1995_SMHI_IFCB_version_2025-03-09.zip",
                "SHARK_Phytoplankton_2000_SMHI_IFCB_version_2023-04-27.zip",
            },
            {"SHARK_Phytoplankton_1995_SMHI_IFCB_version_2024-01-01.zip"},
        ),  # Older version is moved, other datasets are left alone
        (
            [
                "SHARK_Phytoplankton_1995_SMHI_IFCB_version_2024-01-01.zip",
                "SHARK_Phytoplankton_1995_SMHI_IFCB_version_2026-10-13.zip",
            ],
            [
                SharkDataset(
                    name="SHARK_Phytoplankton_1995_SMHI_IFCB",
                    datatype="Phytoplankton",
                    version="2024-01-01",
                    file_name="SHARK_Phytoplankton_1995_SMHI_IFCB_version_2024-01-01.zip",
                ),
            ],
            {
                "SHARK_Phytoplankton_1995_SMHI_IFCB_version_2024-01-01.zip",
                "SHARK_Phytoplankton_1995_SMHI_IFCB_version_2026-10-13.zip",
            },
            set(),
        ),  # Newer local version is kept when an older version is listed
        (
            [
                "SHARK_Phytoplankton_1995_SMHI_IFCB_version_2025-03-09.zip",
                "SHARK_Phytoplankton_1995_SMHI_IFCB_extra_version_2024-01-01.zip",
            ],
            [
                SharkDataset(
                    name="SHARK_Phytoplankton_1995_SMHI_IFCB",
                    datatype="Phytoplankton",
                    version="2025-03-09",
                    file_name="SHARK_Phytoplankton_1995_SMHI_IFCB_version_2025-03-09.zip",
                ),
            ],
            {
                "SHARK_Phytoplankton_1995_SMHI_IFCB_version_2025-03-09.zip",
                "SHARK_Phytoplankton_1995_SMHI_IFCB_extra_version_2024-01-01.zip",
            },
            set(),
        ),  # Dataset with a name starting with the same text is not moved
    ),
)
def test_move_outdated_datasets(
    tmp_path,
    given_local_files,
    given_datasets,
    expected_remaining_files,
    expected_moved_files,
):
    # Given a directory with downloaded datasets
    for file_name in given_local_files:
        (tmp_path / file_name).touch()
    # Given a list of the latest datasets

    # When moving outdated datasets
    move_outdated_datasets(given_datasets, tmp_path)

    # Then only outdated versions are moved to the old datasets directory
    old_datasets_dir = tmp_path / OLD_DATASETS_DIR_NAME
    remaining_files = {path.name for path in tmp_path.iterdir() if path.is_file()}
    moved_files = (
        {path.name for path in old_datasets_dir.iterdir()}
        if old_datasets_dir.exists()
        else set()
    )
    assert remaining_files == expected_remaining_files
    assert moved_files == expected_moved_files


def test_remove_partial_downloads(tmp_path):
    # Given a directory with a complete and a partial download
    complete_file = "SHARK_Phytoplankton_1995_SMHI_IFCB_version_2025-03-09.zip"
    partial_file = "SHARK_Phytoplankton_2000_SMHI_IFCB_version_2025-03-09.zip.part"
    (tmp_path / complete_file).touch()
    (tmp_path / partial_file).touch()

    # When removing partial downloads
    remove_partial_downloads(tmp_path)

    # Then only the complete download remains
    remaining_files = {path.name for path in tmp_path.iterdir()}
    assert remaining_files == {complete_file}
