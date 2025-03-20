from pathlib import Path
from typing import Iterable

import yaml


class DwcaTransformData:
    def __init__(self, config_paths: Iterable[Path]):
        self._config_file_list = config_paths
        self._config = {}
        self._load_configs()

    def _load_configs(self) -> None:
        for config_path in self._config_file_list:
            config_path = Path(config_path)
            if config_path.exists() and config_path.suffix == ".yaml":
                if config := yaml.load(
                    config_path.read_text(encoding="utf-8"), yaml.BaseLoader
                ):
                    config_map = {str(c["if"]): c for c in config}
                    self._config |= config_map

    def transform_row(self, row: dict) -> None:
        for config in self._config.values():
            config_keys = set(config["if"].keys())
            if {key: row.get(key, "") for key in config_keys} == config["if"]:
                row |= config["then"]
