#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib


class DwcaFilters:
    """ """

    def __init__(self, filters_file_list):
        """ """
        self.filters_file_list = filters_file_list
        self.filters_dict = {}
        self.filter_include_groups_dict = {}
        self.filter_exclude_groups_dict = {}
        self.load_translate()

    def get_filters_from_source(self, source_field, value):
        """ """
        if self.filters_dict:
            if source_field in self.filters_dict:
                return self.filters_dict[source_field].get(value, value)
        return value

    def get_filters_keys(self):
        """ """
        return self.filters_dict.keys()

    def get_filters(self):
        """ """
        return self.filters_dict

    def get_filter_include_groups(self):
        """ """
        return self.filter_include_groups_dict

    def get_filter_exclude_groups(self):
        """ """
        return self.filter_exclude_groups_dict

    def load_translate(self):
        """ """
        self.filters_dict = {}
        #
        for filters_file in self.filters_file_list:
            filters_file_path = pathlib.Path(filters_file)
            header = []
            if filters_file_path.suffix in [".txt", ".tsv"]:
                # Stored as text file.
                with filters_file_path.open("r", encoding="cp1252") as filters_file:
                    for index, row in enumerate(filters_file):
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
        include_value = row_dict.get("include_value", "").strip()
        exclude_value = row_dict.get("exclude_value", "").strip()
        filter_group_id = row_dict.get("filter_group_id", "").strip()
        # Included values.
        if source_field and include_value:
            if not source_field[0] == "#":
                if source_field not in self.filters_dict:
                    self.filters_dict[source_field] = {}
                if "included_values" not in self.filters_dict[source_field]:
                    self.filters_dict[source_field]["included_values"] = []
                self.filters_dict[source_field]["included_values"].append(include_value)
        # Excluded values.
        if source_field and exclude_value:
            if not source_field[0] == "#":
                if source_field not in self.filters_dict:
                    self.filters_dict[source_field] = {}
                if "excluded_values" not in self.filters_dict[source_field]:
                    self.filters_dict[source_field]["excluded_values"] = []
                self.filters_dict[source_field]["excluded_values"].append(exclude_value)

        # Filter groups. Are used when multiple fields should be checked.
        if source_field and filter_group_id:
            if not source_field[0] == "#":
                if filter_group_id not in self.filter_include_groups_dict:
                    self.filter_include_groups_dict[filter_group_id] = {}
                if filter_group_id not in self.filter_exclude_groups_dict:
                    self.filter_exclude_groups_dict[filter_group_id] = {}
                if include_value:
                    self.filter_include_groups_dict[filter_group_id][source_field] = include_value
                if exclude_value:
                    self.filter_exclude_groups_dict[filter_group_id][source_field] = exclude_value
