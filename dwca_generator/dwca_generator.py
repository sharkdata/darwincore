#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2020-present SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import yaml
import dict2xml
import collections.abc

from dwca_generator import dwca_data_standard

class DwcaGeneratorConfig():
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
        self.translate = {}
        self.filters = {}

    def create_dwca(self):
        """ """
        self.load_config()
        self.load_source_files()

    def load_config(self):
        """ """
        config_path = pathlib.Path(self.config_file)
        with open(config_path) as file:
            self.dwca_config = yaml.load(file, Loader=yaml.FullLoader)

        # "dwcaTarget"
        file_list = self.source_files = self.get_config_files("dwcaTarget")
        self.dwca_target = file_list[0]
        # "sourceFiles"
        self.source_files = self.get_config_files("sourceFiles")
        # "emlDefinitions"
        file_list = self.get_config_files("emlDefinitions")
        self.eml_definitions = self.merge_config_yaml_files(file_list)
        # "dwcaKeys"
        file_list = self.get_config_files("dwcaKeys")
        self.dwca_keys = self.merge_config_yaml_files(file_list)
        # "fieldMapping"
        file_list = self.get_config_files("fieldMapping")
        self.field_mapping = self.merge_config_yaml_files(file_list)
        # "translate"
        file_list = self.get_config_files("translate")
        self.translate = self.merge_config_yaml_files(file_list)
        # "filters"
        file_list = self.get_config_files("filters")
        self.filters = self.merge_config_yaml_files(file_list)

    def generate_eml_content(self):
        """ """
        eml_dict = self.eml_definitions
        # Convert from dictionary to XML rows.
        eml_xml = {}
        eml_xml["dataset"] = eml_dict["dataset"]
        eml_xml["additionalMetadata"] = eml_dict["additionalMetadata"]
        eml_xml_rows = dict2xml.dict2xml(eml_xml, indent = "    ")
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
        eml_content = "\n".join(xml_rows)
        return eml_content

    # def load_source_files(self):
    #     """ """
    #     source_file_list = []
    #     file_path = pathlib.Path()
    #     if "sourceFiles" in self.dwca_config:
    #         source_files = self.dwca_config["sourceFiles"]
    #         if "directory" in source_files:
    #             directory_path = pathlib.Path(file_path, source_files["directory"])
    #         if "files" in source_files:
    #             for file_name in source_files["files"]:
    #                 file_path = pathlib.Path(directory_path, file_name)
    #                 source_file_list.append(str(file_path))
    #     print(source_file_list)

    def get_config_files(self, config_key):
            """ """
            print()
            file_list = []
            file_path = pathlib.Path()
            if config_key in self.dwca_config:
                dwca_keys = self.dwca_config[config_key]
                if "directory" in dwca_keys:
                    dir_path = pathlib.Path(file_path, dwca_keys["directory"])
                if "files" in dwca_keys:
                    for file_name in dwca_keys["files"]:
                        file_path = pathlib.Path(dir_path, file_name)
                        file_list.append(str(file_path))
            return file_list

    def merge_config_yaml_files(self, yaml_file_list):
            """ Merge configurations as defined in the yaml file list order. """
            result_dict = {}
            for file_name in yaml_file_list:
                file_path = pathlib.Path(file_name)
                with open(file_path, encoding="utf8") as file:
                    new_data = yaml.load(file, Loader=yaml.FullLoader)
                    self.dict_deep_update(result_dict, new_data)
            # print(result_dict)
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

