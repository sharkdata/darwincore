#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import logging
import zipfile

import dwca_generator


class DwcaDataSharkStandard:
    """Contains a list of all data rows stored as dictionaries.
    Each row doctionary contains fields both for the internal format and DwC.
    """

    def __init__(self, dwca_gen_config, filters, translate):
        """ """
        # Reference to DwcaGenerator object.
        self.dwca_gen_config = dwca_gen_config
        self.filters = filters
        self.translate = translate
        # List of dictionaries containing all data rows.
        self.row_list = []
        # Lookup dictionary for keys to avoid duplicates.
        self.dwc_short_names_exists_dict = {}
        # Field mapping between internal and DwC fields.
        self.dwc_default_mapping = {}
        # # List of keys for dynamic fields.
        # self.used_dynamic_field_key_list = []

    def get_data_rows(self):
        """ """
        return self.row_list

    def add_shark_dataset(self, dataset_filepath):
        """ Add data from SHARK zipped files. """
        logger = logging.getLogger("dwca_generator")

        logger.info("")
        logger.info("Adding dataset: " + dataset_filepath)

        # Check if data package is marked for production (PROD).
        status_prod = False
        try:
            with zipfile.ZipFile(dataset_filepath) as z:
                with z.open("processed_data/delivery_note.txt", "r") as f:
                    for row in f:
                        row = row.decode("cp1252")
                        row_items = [str(x.strip()) for x in row.split(":")]
                        if len(row_items) >= 2:
                            key = row_items[0]
                            value = row_items[1]
                            if (key.lower() == "status") and (value.lower() == "prod"):
                                status_prod = True
        except Exception as e:
            logger.warning(" - EXCEPTION: failed to read ZIP file: " + str(e))
            logger.error(" - EXCEPTION: failed to read ZIP file: " + str(e))
            return

        if not status_prod:
            logger.info(" - Package NOT status PROD, skipped: " + dataset_filepath)
            return

        try:
            counter_rows = 0
            counter_filtered = 0
            counter_used = 0
            header = []
            # From file in zip to list of rows.
            with zipfile.ZipFile(dataset_filepath) as z:
                with z.open("shark_data.txt", "r") as f:
                    for index, row in enumerate(f):
                        row = row.decode("cp1252")
                        row_items = [str(x.strip()) for x in row.split("\t")]
                        if index == 0:
                            header = row_items
                        else:
                            counter_rows += 1
                            row_dict = dict(zip(header, row_items))

                            # Add debug info.
                            dataset_name = row_dict.get("dataset_name", "")
                            if dataset_name:
                                row_dict["debug_info"] = (
                                    "Dataset" + dataset_name + " Row: " + str(index)
                                )

                            # Check filter. Don't add filtered rows.
                            add_row = True
                            for (
                                filter_column_name,
                                filter_dict,
                            ) in self.filters.get_filters().items():
                                value = row_dict.get(filter_column_name, "")
                                if value:
                                    included_values = filter_dict.get(
                                        "included_values", None
                                    )
                                    excluded_values = filter_dict.get(
                                        "excluded_values", None
                                    )
                                    if included_values and (
                                        value not in included_values
                                    ):
                                        add_row = False
                                    if excluded_values and (value in excluded_values):
                                        add_row = False

                            # Check combinations of fields.

                            # filter_groups = self.filters.get_filter_include_groups()
                            # for group_key, group_value in filter_groups.items():
                            #     for filter_key, filter_value in group_value.items():
                            #         pass # TODO:

                            filter_groups = self.filters.get_filter_exclude_groups()
                            for group_key, group_value in filter_groups.items():
                                number_of_match = 0
                                for filter_key, filter_value in group_value.items():
                                    value = row_dict.get(filter_key, "")
                                    if str(value) == str(filter_value):
                                        number_of_match += 1
                                if number_of_match == len(group_value):
                                    # msg = row_dict["debug_info"] + "   " + group_key + "   " + str(group_value)
                                    # logger.debug(" - Group-exclude: " + msg)
                                    add_row = False

                            # Extra filer. Used for empty values.
                            if add_row:
                                parameter = row_dict.get("parameter", "")
                                if parameter in [
                                    "Sediment redox potential",
                                    "Sediment water content",
                                ]:
                                    value = row_dict.get("value", "")
                                    if value == "":
                                        add_row = False

                            # Add to list.
                            if add_row:
                                # Translate values.
                                for (
                                    key
                                ) in self.translate.get_translate_from_source_keys():
                                    value = row_dict.get(key, "")
                                    if value:
                                        new_value = (
                                            self.translate.get_translate_from_source(
                                                key, value
                                            )
                                        )
                                        if value != new_value:
                                            row_dict[key] = new_value
                                # Append.
                                counter_used += 1
                                self.row_list.append(row_dict.copy())
                            else:
                                counter_filtered += 1
            #
            msg = (
                " - Rows used: "
                + str(counter_used)
                + "   filtered: "
                + str(counter_filtered)
                + "   total: "
                + str(counter_rows)
            )
            logger.info(msg)

        except Exception as e:
            msg = str(dataset_filepath) + str(e)
            logger.warning("Exception: " + msg)

    def cleanup_data(self):
        """ """
        for row_dict in self.row_list:
            delivery_datatype = water_depth_m = row_dict.get("delivery_datatype", "")
            delivery_datatype = delivery_datatype.lower()

            row_dict["dwc_dataset_name"] = self.dwca_gen_config.eml_definitions["dataset"]["title"]

            try:
                sample_date_str = str(row_dict["sample_date"])
                #             row_dict['year'] = sample_date_str[0:4]
                row_dict["month"] = sample_date_str[5:7]
                row_dict["day"] = sample_date_str[8:10]
            except:
                pass

            # Time zone info. (+01:00 or +02:00 (DST=Daylight Savings Time) for Sweden.
            sample_date = row_dict.get("sample_date", "")
            sample_time = row_dict.get("sample_time", "")
            if (sample_date != "") and (sample_time != ""):
                if dwca_generator.is_daylight_savings_time(sample_date):
                    row_dict["sample_time"] = sample_time + "+02:00"
                else:
                    row_dict["sample_time"] = sample_time + "+01:00"

            # Temporary fixes. Should be done in data.
            coefficient = row_dict.get("coefficient", "")
            if coefficient:
                row_dict["coefficient"] = coefficient.replace(",", ".")
            #
            secchi_depth_m = row_dict.get("secchi_depth_m", "")
            if secchi_depth_m:
                row_dict["secchi_depth_m"] = secchi_depth_m.replace("-", "")

            # water_depth_m sample_min_depth_m sample_max_depth_m for ZB.
            # delivery_datatype = water_depth_m = row_dict.get("delivery_datatype", "")
            if delivery_datatype == "zoobenthos":
                water_depth_m = row_dict.get("water_depth_m", "")
                sample_min_depth_m = row_dict.get("sample_min_depth_m", "")
                sample_max_depth_m = row_dict.get("sample_max_depth_m", "")
                if water_depth_m:
                    if (not sample_min_depth_m) and (not sample_max_depth_m):
                        row_dict["sample_min_depth_m"] = water_depth_m
                        row_dict["sample_max_depth_m"] = water_depth_m

    def create_dwca_keys(self):
        """ """
        config_dwca_keys = self.dwca_gen_config.dwca_keys
        for row_dict in self.row_list:
            # Extra keys for the "event.txt" table.
            # for _dwc_event_node_name, dwc_event_node_dict in self.resources.get_event_nodes_keys().items():
            for dwc_event_node_dict in config_dwca_keys["eventTypeKeys"]["event"]:

                dwc_key_name = dwc_event_node_dict.get("keyName", "")
                dwc_key_prefix = dwc_event_node_dict.get("keyPrefix", "")
                key_list = dwc_event_node_dict.get("keyFields", [])
                dwc_id = dwca_generator.create_extra_key(row_dict, key_list)

                # Used to generate short names.
                if dwc_key_name not in self.dwc_short_names_exists_dict:
                    self.dwc_short_names_exists_dict[dwc_key_name] = {}
                    self.dwc_short_names_exists_dict[dwc_key_name]["seq_no"] = 0
                    self.dwc_short_names_exists_dict[dwc_key_name]["short_ids"] = {}

                if (
                    dwc_id
                    not in self.dwc_short_names_exists_dict[dwc_key_name][
                        "short_ids"
                    ].keys()
                ):
                    seq_no = self.dwc_short_names_exists_dict[dwc_key_name]["seq_no"]
                    seq_no += 1
                    self.dwc_short_names_exists_dict[dwc_key_name]["seq_no"] = seq_no
                    self.dwc_short_names_exists_dict[dwc_key_name]["short_ids"][
                        dwc_id
                    ] = seq_no
                #
                seq_no = self.dwc_short_names_exists_dict[dwc_key_name]["short_ids"][
                    dwc_id
                ]
                dwc_id_short = dwc_key_prefix + str(seq_no)
                row_dict[dwc_key_name] = dwc_id_short

            # Extra keys for the "occurrence.txt" table.
            # for _dwc_event_node_name, dwc_event_node_dict in self.resources.get_occurrence_nodes_keys().items():
            for dwc_event_node_dict in config_dwca_keys["eventTypeKeys"]["occurrence"]:

                scientific_name = row_dict.get("scientific_name", "")
                if not scientific_name:
                    continue
                #
                dwc_key_name = dwc_event_node_dict.get("keyName", "")
                dwc_key_prefix = dwc_event_node_dict.get("keyPrefix", "")
                key_list = dwc_event_node_dict.get("keyFields", [])
                dwc_id = dwca_generator.create_extra_key(row_dict, key_list)

                # Used to generate short names.
                if dwc_key_name not in self.dwc_short_names_exists_dict:
                    self.dwc_short_names_exists_dict[dwc_key_name] = {}
                    self.dwc_short_names_exists_dict[dwc_key_name]["seq_no"] = 0
                    self.dwc_short_names_exists_dict[dwc_key_name]["short_ids"] = {}

                if (
                    dwc_id
                    not in self.dwc_short_names_exists_dict[dwc_key_name][
                        "short_ids"
                    ].keys()
                ):
                    seq_no = self.dwc_short_names_exists_dict[dwc_key_name]["seq_no"]
                    seq_no += 1
                    self.dwc_short_names_exists_dict[dwc_key_name]["seq_no"] = seq_no
                    self.dwc_short_names_exists_dict[dwc_key_name]["short_ids"][
                        dwc_id
                    ] = seq_no
                #
                seq_no = self.dwc_short_names_exists_dict[dwc_key_name]["short_ids"][
                    dwc_id
                ]
                dwc_id_short = dwc_key_prefix + str(seq_no)
                row_dict[dwc_key_name] = dwc_id_short

            # Extra keys for the "extendedmeasurementorfact.txt" table.
            parameter = row_dict.get("parameter", "")
            unit = row_dict.get("unit", "")
            dwc_id_emof = dwc_id + ",param:" + parameter + ",unit:" + unit
            row_dict["emof_param_unit_id"] = dwc_id_emof
