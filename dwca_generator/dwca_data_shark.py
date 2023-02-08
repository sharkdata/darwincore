#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import logging
import zipfile
import math

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

                # Load code translations from zip.
                translate_codes = {}
                translate_fields = set()
                translate_header = []
                if "translate_codes.txt" in z.namelist():
                    with z.open("translate_codes.txt", "r") as f:
                        for index, row in enumerate(f):
                            row = row.decode("cp1252")
                            row_items = [str(x.strip()) for x in row.split("\t")]
                            if index == 0:
                                translate_header = row_items
                            else:
                                counter_rows += 1
                                row_dict = dict(zip(translate_header, row_items))
                                # Used parts.
                                field = row_dict.get("field", "")
                                public_value = row_dict.get("public_value", "")
                                code = row_dict.get("code", "")
                                english = row_dict.get("english", "")
                                # bodc_nerc = row_dict.get("bodc_nerc", "")
                                darwincore = row_dict.get("darwincore", "")
                                # Add key and value.
                                if field and public_value:
                                    translate_fields.add(field)
                                    key = field + "<+>" + public_value
                                    value = darwincore
                                    if not value:
                                        value = code + " (" + english + ")"
                                    translate_codes[key] = value

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
                                # Translate from "translate_codes.txt" in zip file.
                                for key in row_dict.keys():
                                    if key in translate_fields:
                                        value = row_dict.get(key, "")
                                        translate_key = key + "<+>" + value
                                        new_value = translate_codes.get(translate_key, value)
                                        row_dict[key] = new_value

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

            row_dict["dwc_dataset_name"] = self.dwca_gen_config.eml_definitions[
                "dataset"
            ]["title"]

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

            # Fix for ZB with size classes.
            if delivery_datatype == "zooplankton":
                size_class = row_dict.get("size_class", "")
                size_min_um = row_dict.get("size_min_um", "")
                size_max_um = row_dict.get("size_max_um", "")
                if size_class == "":
                    if size_min_um and size_max_um:
                        size_string = str(size_min_um) + "-" + str(size_max_um)
                        row_dict["size_class"] = size_string

            # Add sampler_type_code for Seal. Sometimes also use "obspoint".
            if "seal" in delivery_datatype:
                sampler_type_code = row_dict.get("sampler_type_code", "")
                if sampler_type_code == "":
                    pass
                else:
                    obspoint = row_dict.get("obspoint", "")
                    if obspoint == "":
                        row_dict["obspoint"] = sampler_type_code
                row_dict["sampler_type_code"] = "Observers"

            # Use coordinate_uncertainty_m for some data.
            if "seal" in delivery_datatype:
                sample_latitude_dm = row_dict.get("sample_latitude_dm", "")
                sample_longitude_dm = row_dict.get("sample_longitude_dm", "")
                latitude = sample_latitude_dm.replace(" ", "").replace(",", ".")
                longitude = sample_longitude_dm.replace(" ", "").replace(",", ".")
                latitude = math.floor(float(latitude))
                longitude = math.floor(float(longitude))

                # County AB or A or B.
                if ((latitude == 5920) and (longitude == 1801)):
                    row_dict["coordinate_uncertainty_m"] = "150000"
                # County AC.
                if ((latitude == 6349) and (longitude == 2016)):
                    row_dict["coordinate_uncertainty_m"] = "150000"
                # County BD.
                if ((latitude == 6535) and (longitude == 2209)):
                    row_dict["coordinate_uncertainty_m"] = "150000"
                # County C.
                if ((latitude == 5951) and (longitude == 1738)):
                    row_dict["coordinate_uncertainty_m"] = "150000"
                # County D.
                if ((latitude == 5845) and (longitude == 1701)):
                    row_dict["coordinate_uncertainty_m"] = "150000"
                # County E.
                if ((latitude == 5824) and (longitude == 1537)):
                    row_dict["coordinate_uncertainty_m"] = "150000"
                # County F.
                if ((latitude == 5747) and (longitude == 1409)):
                    row_dict["coordinate_uncertainty_m"] = "150000"
                # County H.
                if ((latitude == 5639) and (longitude == 1621)):
                    row_dict["coordinate_uncertainty_m"] = "150000"
                # County I.
                if ((latitude == 5738) and (longitude == 1817)):
                    row_dict["coordinate_uncertainty_m"] = "150000"
                # County K.
                if ((latitude == 5610) and (longitude == 1535)):
                    row_dict["coordinate_uncertainty_m"] = "150000"
                # County X.
                if ((latitude == 6040) and (longitude == 1709)):
                    row_dict["coordinate_uncertainty_m"] = "150000"
                # County Y.
                if ((latitude == 6237) and (longitude == 1756)):
                    row_dict["coordinate_uncertainty_m"] = "150000"

            # For empty observations use "absent" in occurrenceStatus.
            # present_absent = "present"
            if "present_absent" not in row_dict:
                row_dict["present_absent"] = "present"
            #
            if delivery_datatype in ["ringed seal", "ringedseal"]:
                parameter = row_dict.get("parameter", "")
                value = row_dict.get("value", "")
                if parameter in ["# counted", "Calculated # counted", "Abundance"]:
                    value = float(value)
                    if value == 0.0:
                        row_dict["present_absent"] = "absent"
                        scientific_name = row_dict.get("scientific_name", "")
                        if scientific_name == "":
                            row_dict["scientific_name"] = "Pusa hispida"
                            row_dict["aphia_id"] = "159021"
            #
            if delivery_datatype in ["picoplankton"]:
                parameter = row_dict.get("parameter", "")
                value = row_dict.get("value", "")
                if parameter in ["# counted", "Abundance", "Biovolume concentration", "Carbon concentration"]:
                    value = float(value)
                    if value == 0.0:
                        row_dict["present_absent"] = "absent"
                        scientific_name = row_dict.get("scientific_name", "")
                        if scientific_name == "":
                            row_dict["scientific_name"] = "Biota"

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

                size_class = row_dict.get("size_class", "")
                if size_class:
                    dwc_id_short += "-SIZECLASS-" + size_class
                else:
                    cell_volume = row_dict.get("reported_cell_volume_um3", "")
                    if cell_volume:
                        dwc_id_short += "-CELLVOLUME-" + cell_volume.replace(",", ".")

                row_dict[dwc_key_name] = dwc_id_short

            # Extra keys for the "extendedmeasurementorfact.txt" table.
            parameter = row_dict.get("parameter", "")
            unit = row_dict.get("unit", "")
            dwc_id_emof = dwc_id + ",param:" + parameter + ",unit:" + unit
            row_dict["emof_param_unit_id"] = dwc_id_emof
