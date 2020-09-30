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
        self.dwca_config = {}
        self.source_rows = []

    def create_dwca(self):
        """ """
        self.load_config()
        self.load_source_files()

    def load_config(self):
        """ """
        config_path = pathlib.Path(self.config_file)
        with open(config_path) as file:
            self.dwca_config = yaml.load(file, Loader=yaml.FullLoader)

    def load_source_files(self):
        """ """
        file_path = pathlib.Path()
        if "importFileGroups" in self.dwca_config:
            import_file_groups = self.dwca_config["importFileGroups"]
            for import_file_group in import_file_groups:
                if "directory" in import_file_group:
                    file_path = pathlib.Path(file_path, import_file_group["directory"])
                if "files" in import_file_group:
                    for file_name in import_file_group["files"]:
                        file_path = pathlib.Path(file_path, file_name)

                        print("DEBUG: Processing ", file_path)

                        # with open(file_path, encoding="utf8") as file:
                        #     dwca_new_data = yaml.load(file, Loader=yaml.FullLoader)
                        #     dict_deep_update(eml_dict, dwca_new_data)

    def load_create_keys(self):
        """ """

    def load_create_eml(self):
        """ """
        eml_dict = {}
        # Read and merge EML definition files.
        yaml_path = pathlib.Path()
        if "emlDefinitions" in self.dwca_config:
            eml_definitions = self.dwca_config["emlDefinitions"]
            if "directory" in eml_definitions:
                yaml_path = pathlib.Path(yaml_path, eml_definitions["directory"])
            if "files" in eml_definitions:
                for yaml_file in eml_definitions["files"]:
                    yaml_file_path = pathlib.Path(yaml_path, yaml_file)
                    with open(yaml_file_path, encoding="utf8") as file:
                        # print("DEBUG: Processing ", file)
                        dwca_new_data = yaml.load(file, Loader=yaml.FullLoader)
                        dict_deep_update(eml_dict, dwca_new_data)
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
        # Directory and filename for the EML.XML file.
        target_config = self.dwca_config.get("dwcaTarget", {}) 
        target_dir = target_config.get("directory", "")
        target_file = target_config.get("file", "")
        eml_xml_path = pathlib.Path(target_file)
        if target_dir:
            target_path = pathlib.Path(target_dir)
            if not target_path.exists():
                target_path.mkdir(parents=True)
            eml_xml_path = pathlib.Path(target_path, target_file)
        # Write EML.XLM
        with eml_xml_path.open("w", encoding="utf8") as out_file:
            out_file.write("\n".join(xml_rows))


def dict_deep_update(target, updates):
    """ Recursively updates or extends a dict. """
    for key, value in updates.items():
        if value == "REMOVE":
            del target[key]
        elif isinstance(value, collections.abc.Mapping):
            target[key] = dict_deep_update(target.get(key, {}), value)
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
        dwca_generator.load_source_files()
        dwca_generator.load_create_eml()
