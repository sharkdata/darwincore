#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2020-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
from collections import namedtuple

import yaml
import dict2xml
import collections.abc

from dwca_generator.dwca_utils import config_with_suffix


FileWithPrefix = namedtuple("FileWithPrefix", ("file", "prefix"))


class DwcaGeneratorConfig:
    """ """

    def __init__(self, config_file):
        """ """
        self.config_file = config_file
        self.clear()

    def clear(self):
        """ """
        self.dwca_config = {}
        self.dwca_target = ""
        self.source_files = []
        self.eml_definitions = {}
        self.dwca_keys = {}
        self.field_mapping = {}
        self.taxa_worms_file = ""
        self.translate_files = []
        self.filters_files = []
        self.metadata_source = None
        self.metadata_template = None
        self.metadata_target = None

    # def create_dwca(self):
    #     """ """
    #     self.load_config()
    #     self.load_source_files()

    def load_config(self):
        """ """
        config_path = pathlib.Path(self.config_file)
        with open(config_path) as file:
            self.dwca_config = yaml.load(file, Loader=yaml.FullLoader)

        # "dwcaTarget"
        file_list = self.source_files = self.get_config_files("dwcaTarget")
        self.dwca_target = file_list[0] if len(file_list) > 0 else ""
        # "sourceFiles"
        self.source_files = self.load_source_files()
        # "emlDefinitions"
        file_list = self.get_config_files("emlDefinitions")
        self.eml_definitions = self.merge_config_yaml_files(file_list)
        # "dwcaKeys"
        file_list = self.get_config_files("dwcaKeys")
        self.dwca_keys = self.merge_config_yaml_files(file_list)
        # "fieldMapping"
        file_list = self.get_config_files("fieldMapping", include_prefix=True)
        self.field_mapping = self.merge_config_yaml_files(file_list)
        # "taxaWorms"
        file_list = self.get_config_files("taxaWorms")
        self.taxa_worms_file = file_list[0] if len(file_list) > 0 else ""
        # "translate"
        self.translate_files = self.get_config_files("translate")
        # "filters"
        self.filters_files = self.get_config_files("filters")
        # "metadataSourceFiles"
        file_list = self.get_config_files("metadataSourceFiles")
        metadata = self.merge_config_yaml_files(file_list)
        self.metadata_source = self.cleanup_metadata(metadata)
        # "metadataTemplate"
        file_list = self.get_config_files("metadataTemplate")
        self.metadata_template = file_list[0] if len(file_list) > 0 else ""
        # "metadataTarget"
        file_list = self.get_config_files("metadataTarget")
        self.metadata_target = file_list[0] if len(file_list) > 0 else ""

    def generate_eml_content(self):
        """ """
        eml_dict = self.eml_definitions

        # print(eml_dict["dataset"]["intellectualRights"])

        # Convert from dictionary to XML rows.
        eml_xml = {}
        eml_xml["dataset"] = eml_dict["dataset"]
        eml_xml["additionalMetadata"] = eml_dict["additionalMetadata"]
        eml_xml_rows = dict2xml.dict2xml(eml_xml, indent="    ")
        # Append header and footer.
        xml_rows = []
        for row in eml_dict.get("emlHeader", []):
            xml_rows.append(row)
        xml_rows.append("")
        for row in eml_xml_rows.splitlines():
            xml_rows.append(row)
        for row in eml_dict.get("emlFooter", []):
            xml_rows.append(row)
        #
        # eml_content = "\n".join(xml_rows)
        # return eml_content
        return xml_rows

    def load_source_files(self):
        """ """
        source_file_list = []
        file_path = pathlib.Path()
        if "sourceFiles" in self.dwca_config:
            source_files = self.dwca_config["sourceFiles"]
            if "directory" in source_files:
                directory_path = pathlib.Path(file_path, source_files["directory"])
            if "globSearch" in source_files:
                globSearch = source_files["globSearch"]
                for file_path in pathlib.Path(directory_path).glob(globSearch):
                    if file_path not in source_file_list:
                        source_file_list.append(str(file_path))
            if "files" in source_files:
                for file_name in source_files["files"]:
                    file_path = pathlib.Path(directory_path, file_name)
                    if file_path not in source_file_list:
                        source_file_list.append(str(file_path))
        # print("\nFiles to process: ")
        # print("\n".join(sorted(source_file_list)))
        return sorted(source_file_list)

    def get_config_files(self, config_key, include_prefix=False) -> list[str] | list[FileWithPrefix]:
        """ """
        file_list = []
        if config_key in self.dwca_config:
            dwca_keys = self.dwca_config[config_key]

            dir_path = pathlib.Path()
            if "directory" in dwca_keys:
                dir_path /= dwca_keys["directory"]

            if "files" in dwca_keys:
                for config_file in dwca_keys["files"]:
                    if isinstance(config_file, str):
                        suffix = None
                    else:
                        config_file, suffix = config_file

                    config_file = str(dir_path / config_file)

                    if include_prefix:
                        config_file = FileWithPrefix(config_file, suffix)
                    file_list.append(config_file)
        return file_list

    def merge_config_yaml_files(self, yaml_file_list: list[str] | list[FileWithPrefix]):
        """ Merge configurations as defined in the yaml file list order. """
        result_dict = {}
        for file_name in yaml_file_list:
            if isinstance(file_name, FileWithPrefix):
                file_name, suffix = file_name
            else:
                suffix = None
            file_path = pathlib.Path(file_name)
            with open(file_path, encoding="utf8") as file:
                new_data = yaml.load(file, Loader=yaml.FullLoader)
                new_data = config_with_suffix(new_data, suffix)
                result_dict |= new_data

        return result_dict

    def dict_deep_update(self, target, updates):
        """ Recursively updates or extends a dict. """
        for key, value in updates.items():
            if value == "REMOVE":
                del target[key]
            elif isinstance(value, collections.abc.Mapping):
                target[key] = self.dict_deep_update(target.get(key, {}), value)
            else:
                target[key] = value
        return target

    def cleanup_metadata(self, metadata):
        """ """
        new_metadata = self.stripValues(metadata)
        return new_metadata

    def stripValues(self, data):
        if isinstance(data, dict):
            # return {k:self.stripValues(v) for k, v in data.items() if k is not None and v is not None}
            return {k: self.stripValues(v) for k, v in data.items()}
        elif isinstance(data, list):
            # return [self.stripValues(item) for item in data if item is not None]
            return [self.stripValues(item) for item in data]
        elif isinstance(data, tuple):
            # return tuple(self.stripValues(item) for item in data if item is not None)
            return tuple(self.stripValues(item) for item in data)
        elif isinstance(data, set):
            # return {self.stripValues(item) for item in data if item is not None}
            return {self.stripValues(item) for item in data}
        else:
            # return data
            if isinstance(data, str):
                return data.strip()
            else:
                return data

