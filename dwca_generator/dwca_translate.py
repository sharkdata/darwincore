#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2020-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib


class DwcaTranslate:
    """ """

    def __init__(self, translate_file_list):
        """ """
        self.translate_file_list = translate_file_list
        self.translate_from_source_dict = {}
        self.translate_from_dwc_dict = {}
        self.load_translate()

    def get_translate_from_source(self, source_field, value):
        """ """
        if self.translate_from_source_dict:
            if source_field in self.translate_from_source_dict:
                return self.translate_from_source_dict[source_field].get(value, value)
        return value

    def get_translate_from_dwc(self, dwc_field, value):
        """ """
        if self.translate_from_dwc_dict:
            if dwc_field in self.translate_from_dwc_dict:
                return self.translate_from_dwc_dict[dwc_field].get(value, value)
        return value

    def get_translate_from_source_keys(self):
        """ """
        return self.translate_from_source_dict.keys()

    def get_translate_from_dwc_keys(self):
        """ """
        return self.translate_from_dwc_dict.keys()

    def load_translate(self):
        """ """
        self.translate_dict = {}
        #
        for translate_file in self.translate_file_list:
            translate_file_path = pathlib.Path(translate_file)
            header = []
            if translate_file_path.suffix in [".txt", ".tsv"]:
                # Stored as text file.
                # with translate_file_path.open("r", encoding="cp1252") as translate_file:
                with translate_file_path.open("r", encoding="utf8") as translate_file:
                    for index, row in enumerate(translate_file):
                        row = [item.strip() for item in row.split("\t")]
                        if index == 0:
                            header = row
                        else:
                            if len(row) >= 2:
                                row_dict = dict(zip(header, row))
                                self.add_fields_to_dict(row_dict)

    def add_fields_to_dict(self, row_dict):
        """ """
        source_field = row_dict.get("source_field", "").strip()
        dwc_field = row_dict.get("dwc_field", "").strip()
        from_value = row_dict.get("from_value", "").strip()
        to_value = row_dict.get("to_value", "").strip()

        if source_field and from_value:
            if source_field not in self.translate_from_source_dict:
                self.translate_from_source_dict[source_field] = {}
            self.translate_from_source_dict[source_field][from_value] = to_value

        if dwc_field and from_value:
            if dwc_field not in self.translate_from_dwc_dict:
                self.translate_from_dwc_dict[dwc_field] = {}
            self.translate_from_dwc_dict[dwc_field][from_value] = to_value
