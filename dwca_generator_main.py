#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2020-present SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import yaml
import dict2xml
import collections.abc

class DwcaGenerator():
    """ """

    def __init__(self, config_file):
        """ """
        self.config_file = config_file

    def clear(self):
        """ """
        self.dwca_config = {}
        self.dwca_target = ""
        self.source_files = {}
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

        # dwca_generator.load_dwca_target()
        file_list = self.source_files = self.get_config_files("dwcaTarget")
        self.dwca_target = file_list[0]
        # dwca_generator.load_source_files()
        self.source_files = self.get_config_files("sourceFiles")
        # dwca_generator.load_eml_definitions()
        file_list = self.get_config_files("emlDefinitions")
        self.eml_definitions = self.merge_config_yaml_files(file_list)
        # dwca_generator.load_dwca_keys()
        file_list = self.get_config_files("dwcaKeys")
        self.dwca_keys = self.merge_config_yaml_files(file_list)
        # dwca_generator.load_field_mapping()
        file_list = self.get_config_files("fieldMapping")
        self.field_mapping = self.merge_config_yaml_files(file_list)
        # dwca_generator.load_translate()
        file_list = self.get_config_files("translate")
        self.translate = self.merge_config_yaml_files(file_list)
        # dwca_generator.load_filters()
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
        # # Directory and filename for the EML.XML file.
        # target_config = self.dwca_config.get("dwcaTarget", {}) 
        # target_dir = target_config.get("directory", "")
        # target_file = target_config.get("file", "")
        # eml_xml_path = pathlib.Path(target_file)
        # if target_dir:
        #     target_path = pathlib.Path(target_dir)
        #     if not target_path.exists():
        #         target_path.mkdir(parents=True)
        #     eml_xml_path = pathlib.Path(target_path, target_file)
        # # Write EML.XLM
        # with eml_xml_path.open("w", encoding="utf8") as out_file:
        #     out_file.write("\n".join(xml_rows))
        
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

    # def load_dwca_keys(self):
    #     """ """
    #     dwca_keys_dict = {}
    #     file_path = pathlib.Path()
    #     if "dwcaKeys" in self.dwca_config:
    #         dwca_keys = self.dwca_config["dwcaKeys"]
    #         if "directory" in dwca_keys:
    #             file_path = pathlib.Path(file_path, dwca_keys["directory"])
    #         if "files" in dwca_keys:
    #             for file_name in dwca_keys["files"]:
    #                 file_path = pathlib.Path(file_path, file_name)
    #                 with open(file_path, encoding="utf8") as file:
    #                     new_data = yaml.load(file, Loader=yaml.FullLoader)
    #                     dict_deep_update(dwca_keys_dict, new_data)
    #     print(dwca_keys_dict)

    # def load_eml_definitions(self):
    #     """ """
    #     eml_dict = {}
    #     # Read and merge EML definition files.
    #     yaml_path = pathlib.Path()
    #     if "emlDefinitions" in self.dwca_config:
    #         eml_definitions = self.dwca_config["emlDefinitions"]
    #         if "directory" in eml_definitions:
    #             yaml_path = pathlib.Path(yaml_path, eml_definitions["directory"])
    #         if "files" in eml_definitions:
    #             for yaml_file in eml_definitions["files"]:
    #                 yaml_file_path = pathlib.Path(yaml_path, yaml_file)
    #                 with open(yaml_file_path, encoding="utf8") as file:
    #                     # print("DEBUG: Processing ", file)
    #                     new_data = yaml.load(file, Loader=yaml.FullLoader)
    #                     dict_deep_update(eml_dict, new_data)
    #     # Convert from dictionary to XML rows.
    #     eml_xml = {}
    #     eml_xml["dataset"] = eml_dict["dataset"]
    #     eml_xml["additionalMetadata"] = eml_dict["additionalMetadata"]
    #     eml_xml_rows = dict2xml.dict2xml(eml_xml, indent = "    ")
    #     # Append header and footer.
    #     xml_rows = []
    #     for row in eml_dict.get("emlHeader", []):
    #         xml_rows.append(row)
    #     xml_rows.append("")
    #     for row in eml_xml_rows.splitlines():
    #         xml_rows.append(row)
    #     for row in eml_dict.get("emlFooter", []):
    #         xml_rows.append(row)
    #     # Directory and filename for the EML.XML file.
    #     target_config = self.dwca_config.get("dwcaTarget", {}) 
    #     target_dir = target_config.get("directory", "")
    #     target_file = target_config.get("file", "")
    #     eml_xml_path = pathlib.Path(target_file)
    #     if target_dir:
    #         target_path = pathlib.Path(target_dir)
    #         if not target_path.exists():
    #             target_path.mkdir(parents=True)
    #         eml_xml_path = pathlib.Path(target_path, target_file)
    #     # Write EML.XLM
    #     with eml_xml_path.open("w", encoding="utf8") as out_file:
    #         out_file.write("\n".join(xml_rows))

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
            print(result_dict)
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


if __name__ == "__main__":
    """ """

    config_files = [
        "dwca_config/dwca_bacterioplankton_nat.yaml",
        # config_file = "dwca_config/dwca_bacterioplankton_nat.yaml",
        # config_file = "dwca_config/dwca_bacterioplankton_nat.yaml",
    ]
    
    for config_file in config_files:
        dwca_generator = DwcaGenerator(config_file)
        dwca_generator.load_config()
        eml_content = dwca_generator.generate_eml_content()
        print(eml_content)

        # TEST
        eml_xml_path = pathlib.Path(dwca_generator.dwca_target)
        # Write EML.XLM
        with eml_xml_path.open("w", encoding="utf8") as out_file:
            out_file.write(eml_content)
