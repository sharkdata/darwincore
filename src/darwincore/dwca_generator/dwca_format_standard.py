#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import csv
import logging
from pathlib import Path

import darwincore
from darwincore.dwca_generator import dwca_meta_xml, dwca_utils
from darwincore.dwca_generator.dwca_transform_data import DwcaTransformData


class DwcaFormatStandard(object):
    """ """

    def __init__(
        self, data, dwca_gen_config, worms_info, translate, transform: DwcaTransformData
    ):
        """Darwin Core Archive Format base class."""

        self.target_dwca_path = Path(dwca_gen_config.dwca_target)
        self.data_object = data
        self.dwca_gen_config = dwca_gen_config
        self.worms_info_object = worms_info
        self.translate = translate
        self.transform = transform
        self.clear()
        self.source_rows = self.data_object.get_data_rows()

    def clear(self):
        """ """
        self.source_rows = []
        self.dwca_event = []
        self.dwca_occurrence = []
        self.dwca_measurementorfact = []
        self._taxa_lookup_dict = {}

    def create_dwca_event(self):
        """ """
        # Create control dictionary.
        event_keys = self.dwca_gen_config.dwca_keys["eventTypeKeys"]["event"]
        dwca_node_names = [event_dict["eventType"] for event_dict in event_keys]
        event_control_dict = {}
        for index, dwca_node_name in enumerate(dwca_node_names):
            event_control_dict[dwca_node_name] = {}
            event_control_dict[dwca_node_name]["used_key_list"] = (
                set()
            )  # To avoid duplicates.
            event_control_dict[dwca_node_name]["dwc_key_name"] = event_keys[index][
                "keyName"
            ]

        # Process all data rows.
        for source_row in self.source_rows:
            # Check if marked for removal.
            if source_row.get("remove_row", "") == "REMOVE":
                continue
            # Iterate over nodes.
            for dwca_node_name in dwca_node_names:
                # Current row in control dictionary.
                control_dict = event_control_dict[dwca_node_name]
                # Get keys.
                node_key = source_row.get(control_dict["dwc_key_name"], "")
                # parent_node_key = source_row.get(control_dict['dwc_event_key_name'], '')
                # Create event row.
                if node_key and (node_key not in control_dict["used_key_list"]):
                    control_dict["used_key_list"].add(node_key)
                    #
                    event_dict = {}
                    # Add basics.
                    event_dict["id"] = node_key
                    event_dict["eventType"] = dwca_node_name
                    # event_dict['eventID'] = node_key
                    # event_dict['parentEventID'] = parent_node_key

                    event_content_list = self.dwca_gen_config.field_mapping[
                        "dwcaEventContent"
                    ]
                    for event_content in event_content_list:
                        if dwca_node_name != event_content.get("eventType", ""):
                            continue
                        # Add content.
                        self.add_content(event_content, source_row, event_dict)

                        # Check if sampleSizeValue is empty and if so make sampleSizeUnit
                        # empty too
                    if not event_dict.get("sampleSizeValue"):
                        event_dict["sampleSizeUnit"] = ""

                        # Append event row content.
                    self.dwca_event.append(event_dict.copy())

    def create_dwca_occurrence(self):
        """ """
        # Create control dictionary.
        occurrence_keys = self.dwca_gen_config.dwca_keys["eventTypeKeys"]["occurrence"]
        dwca_node_names = [
            occurrence_key["eventType"] for occurrence_key in occurrence_keys
        ]
        occurrence_control_dict = {}
        for index, dwca_node_name in enumerate(dwca_node_names):
            occurrence_control_dict[dwca_node_name] = {}
            occurrence_control_dict[dwca_node_name]["used_key_list"] = (
                set()
            )  # To avoid duplicates.
            occurrence_control_dict[dwca_node_name]["dwc_key_name"] = occurrence_keys[
                index
            ]["keyName"]

        aphia_id_mapping = _read_aphia_id_mapping()

        # Process all data rows.
        for source_row in self.source_rows:
            # Check if marked for removal.
            if source_row.get("remove_row", "") == "REMOVE":
                continue
            # Iterate over nodes.
            for dwca_node_name in dwca_node_names:
                if dwca_node_name not in occurrence_control_dict:
                    continue
                # Current row in control dictionary.
                control_dict = occurrence_control_dict[dwca_node_name]
                # Get keys.
                node_key = source_row.get(control_dict["dwc_key_name"], "")
                # event_node_key = source_row.get(control_dict['dwc_event_key_name'], '')
                # Create event row.
                if node_key and (node_key not in control_dict["used_key_list"]):
                    control_dict["used_key_list"].add(node_key)
                    #
                    occurrence_dict = {}
                    # Add basics.
                    # occurrence_dict['id'] = event_node_key
                    # occurrence_dict['eventID'] = event_node_key
                    occurrence_dict["occurrenceID"] = node_key

                    content_list = self.dwca_gen_config.field_mapping[
                        "dwcaOccurrenceContent"
                    ]
                    for content in content_list:
                        if dwca_node_name != content.get("eventType", ""):
                            continue

                        # Add taxa info.
                        aphia_id = source_row.get("aphia_id", "")
                        scientific_name = source_row.get("scientific_name", "")

                        # Try to add missing AphiaID from add_aphia_id_taxon.txt
                        if not aphia_id:
                            aphia_id = aphia_id_mapping.get(scientific_name, "")

                        worms_info_dict = self.worms_info_object.get_worms_info(
                            aphia_id, scientific_name
                        )
                        source_row.update(worms_info_dict)

                        # Create LSID for Phytoplankton BVOL data.
                        bvol_aphia_id = source_row.get("bvol_aphia_id", "")
                        if bvol_aphia_id:
                            bvol_aphia_lsid = (
                                "https://www.marinespecies.org/aphia.php?p=taxdetails&id="
                                + bvol_aphia_id
                            )
                            source_row["bvol_aphia_lsid"] = bvol_aphia_lsid

                        # Add content.
                        self.add_content(content, source_row, occurrence_dict)

                        # Phytoplankton fix
                        if (
                            all(
                                key in occurrence_dict
                                and "SHARK_Phytoplankton"
                                in occurrence_dict.get("dynamicProperties", "")
                                for key in (
                                    "dynamicProperties",
                                    "scientificName",
                                    "verbatimIdentification",
                                    "scientificNameID",
                                )
                            )
                            and occurrence_dict.get("scientificName")
                            == "Bacillariophyceae"
                            and occurrence_dict.get("verbatimIdentification")
                            == "Pennales"
                            and "1304629" in occurrence_dict.get("scientificNameID", "")
                        ):
                            occurrence_dict["scientificName"] = "Pennales"

                        worms_lsid = occurrence_dict.get("scientificNameID", "")
                        if worms_lsid.isnumeric():
                            worms_lsid_new = (
                                "urn:lsid:marinespecies.org:taxname:" + worms_lsid
                            )
                            occurrence_dict["scientificNameID"] = worms_lsid_new

                        # Append occurrence row content.
                        self.dwca_occurrence.append(occurrence_dict.copy())

    def create_dwca_measurementorfact(self):
        """ """
        logger = logging.getLogger("dwca_generator")
        # For checking for duplicates.
        used_mof_occurrence_key_list = set()
        duplicate_row_number = 0

        # Create control dictionary.
        emof_keys = self.dwca_gen_config.dwca_keys["eventTypeKeys"]["emof"]
        dwca_node_names = [event_dict["eventType"] for event_dict in emof_keys]
        emof_control_dict = {}
        for index, dwca_node_name in enumerate(dwca_node_names):
            emof_control_dict[dwca_node_name] = {}
            emof_control_dict[dwca_node_name]["used_key_list"] = set()
            emof_control_dict[dwca_node_name]["dwc_key_name"] = emof_keys[index][
                "keyName"
            ]
            emof_control_dict[dwca_node_name]["dwc_event_key_name"] = emof_keys[index][
                "eventKeyName"
            ]

        # Process all data rows.
        for source_row in self.source_rows:
            # Check if marked for removal.
            if source_row.get("remove_row", "") == "REMOVE":
                continue
            # Check for duplicates.
            emof_param_unit_id = source_row.get("emof_param_unit_id", "")
            if emof_param_unit_id and (
                emof_param_unit_id not in used_mof_occurrence_key_list
            ):
                used_mof_occurrence_key_list.add(emof_param_unit_id)

                # Iterate over nodes.
                for dwca_node_name in dwca_node_names:
                    if dwca_node_name not in emof_control_dict:
                        continue
                    # Current row in control dictionary.
                    control_dict = emof_control_dict[dwca_node_name]
                    # Get keys.
                    event_node_key = source_row.get(
                        control_dict["dwc_event_key_name"], ""
                    )
                    # Create event row.
                    emof_dict = {}
                    # Add basics.
                    emof_dict["id"] = event_node_key
                    emof_dict["eventID"] = event_node_key

                    content_list = self.dwca_gen_config.field_mapping["dwcaEmofContent"]
                    for content in content_list:
                        if dwca_node_name != content.get("eventType", ""):
                            continue

                        # Add content.
                        self.add_content(content, source_row, emof_dict)

                        # Append.
                        if emof_dict.get("measurementType", ""):
                            # Measurement identifiers. NERC vocabular.
                            # nerc codes found at https://vocab.nerc.ac.uk/collection/P01/current/
                            unit = emof_dict.get("measurementUnit", "")
                            measurement_method = emof_dict.get("measurementMethod", "")

                            # nerc codes found at https://vocab.nerc.ac.uk/collection/P06/current/
                            if (
                                unit == "ind/analysed sample fraction"
                                and measurement_method != "Image analysis"
                            ):
                                emof_dict["measurementUnit"] = (
                                    "Dimensionless"
                                )

                            self.dwca_measurementorfact.append(emof_dict.copy())

                        # Get key.
                        event_node_key = source_row.get(control_dict["dwc_key_name"], "")
                        # Create event row.
                        if event_node_key and (
                            event_node_key not in control_dict["used_key_list"]
                        ):
                            control_dict["used_key_list"].add(event_node_key)

                            if "extraMeasurements" in content:
                                extraMeasurements = content["extraMeasurements"]
                                for extraMeasurement in extraMeasurements:
                                    param = extraMeasurement.get("measurementType", "")
                                    param_id = extraMeasurement.get(
                                        "measurementTypeID", ""
                                    )
                                    unit = extraMeasurement.get("measurementUnit", "")
                                    unit_id = extraMeasurement.get(
                                        "measurementUnitID", ""
                                    )
                                    source_key = extraMeasurement.get("sourceKey", "")
                                    value = source_row.get(source_key, "")
                                    value_id = extraMeasurement.get(
                                        "measurementValueID", ""
                                    )

                                    if "text" in extraMeasurement.keys():
                                        value = extraMeasurement.get("text", "")
                                    if param and (value not in [""]):
                                        if param_id is None:
                                            param_id = ""
                                        if unit is None:
                                            unit = ""
                                        if unit_id is None:
                                            unit_id = ""
                                        emof_dict["measurementType"] = param
                                        emof_dict["measurementTypeID"] = param_id
                                        emof_dict["measurementValue"] = value
                                        emof_dict["measurementUnit"] = unit
                                        emof_dict["measurementUnitID"] = unit_id
                                        emof_dict["measurementValueID"] = value_id

                                        if (
                                            param == "Sampling laboratory name"
                                            and value
                                            == "Swedish Meteorological and Hydrological "
                                            "Institute"
                                        ):
                                            emof_dict["measurementValueID"] = (
                                                "https://edmo.seadatanet.org/report/545"
                                            )

                                        elif (
                                            param == "Analytical laboratory name"
                                            and value
                                            == "Swedish Meteorological and Hydrological "
                                            "Institute"
                                        ):
                                            emof_dict["measurementValueID"] = (
                                                "https://edmo.seadatanet.org/report/545"
                                            )
                                        elif (
                                            param == "Sampling laboratory name"
                                            and value
                                            == "Swedish Museum of Natural History"
                                        ):
                                            emof_dict["measurementValueID"] = (
                                                "https://edmo.seadatanet.org/report/614"
                                            )

                                        elif (
                                            param == "Analytical laboratory name"
                                            and value
                                            == "Swedish Museum of Natural History"
                                        ):
                                            emof_dict["measurementValueID"] = (
                                                "https://edmo.seadatanet.org/report/614"
                                            )
                                        elif (
                                            param == "Sampling laboratory name"
                                            and value
                                            == "Swedish Environmental Protection Agency"
                                        ):
                                            emof_dict["measurementValueID"] = (
                                                "https://edmo.seadatanet.org/report/1353"
                                            )

                                        elif (
                                            param == "Analytical laboratory name"
                                            and value
                                            == "Swedish Environmental Protection Agency"
                                        ):
                                            emof_dict["measurementValueID"] = (
                                                "https://edmo.seadatanet.org/report/1353"
                                            )

                                        elif (
                                            param == "Imaging instrument name"
                                            or param == "Sampler type"
                                        ) and value == "IFCB":
                                            emof_dict["measurementValueID"] = (
                                                "http://vocab.nerc.ac.uk/collection/L22/current/TOOL1588/"
                                            )

                                        elif (
                                            param == "Trophic type"
                                            and value == "Mixotrophic"
                                        ):
                                            emof_dict["measurementValueID"] = (
                                                "http://vocab.nerc.ac.uk/collection/S13/current/S1314/"
                                            )

                                        elif (
                                            param == "Trophic type"
                                            and value == "Heterotrophic"
                                        ):
                                            emof_dict["measurementValueID"] = (
                                                "http://vocab.nerc.ac.uk/collection/S13/current/S1312/"
                                            )

                                        elif (
                                            param == "Trophic type"
                                            and value == "Autotrophic"
                                        ):
                                            emof_dict["measurementValueID"] = (
                                                "http://vocab.nerc.ac.uk/collection/S13/current/S135/"
                                            )
                                        elif (
                                            param == "Sampler type"
                                            and value == "Van Veen grab"
                                        ):
                                            emof_dict["measurementValueID"] = (
                                                "http://vocab.nerc.ac.uk/collection/L22/current/TOOL0653/"
                                            )
                                        elif (
                                            param == "Sampler type"
                                            and value == "Smith McIntyre Grab"
                                        ):
                                            emof_dict["measurementValueID"] = (
                                                "http://vocab.nerc.ac.uk/collection/L22/current/TOOL0962/"
                                            )

                                        elif param == "Sampling platform":
                                            mapping = {
                                                "77SE": "http://vocab.nerc.ac.uk/collection/C17/current/77SE/",
                                                "77AR": "http://vocab.nerc.ac.uk/collection/C17/current/77AR/",
                                                "34AR": "http://vocab.nerc.ac.uk/collection/C17/current/34AR/",
                                                "77KB": "http://vocab.nerc.ac.uk/collection/C17/current/77KB/",
                                                "77KC": "http://vocab.nerc.ac.uk/collection/C17/current/77KC/",
                                                "77NE": "http://vocab.nerc.ac.uk/collection/C17/current/77NE/",
                                                "77SN": "http://vocab.nerc.ac.uk/collection/C17/current/77SN/",
                                                "77SN": "http://vocab.nerc.ac.uk/collection/C17/current/77SN/",
                                                "77UR": "http://vocab.nerc.ac.uk/collection/C17/current/77UR/",
                                                "77FY": "http://vocab.nerc.ac.uk/collection/C17/current/77FY/",
                                                "77SU": "http://vocab.nerc.ac.uk/collection/C17/current/77SU/",
                                                "77LT": "http://vocab.nerc.ac.uk/collection/C17/current/77LT/",
                                                "77LA": "http://vocab.nerc.ac.uk/collection/C17/current/77LA/",
                                                "77K5": "http://vocab.nerc.ac.uk/collection/C17/current/77K5/",
                                                "77TH": "http://vocab.nerc.ac.uk/collection/C17/current/77TH/",
                                                "77NC": "http://vocab.nerc.ac.uk/collection/C17/current/77NC/",
                                                "77K4": "http://vocab.nerc.ac.uk/collection/C17/current/77K4/",
                                                "77KA": "http://vocab.nerc.ac.uk/collection/C17/current/77KA/",
                                                "77LY": "http://vocab.nerc.ac.uk/collection/C17/current/77LY/",
                                                "77VA": "http://vocab.nerc.ac.uk/collection/C17/current/77VA/",
                                                "77SK": "http://vocab.nerc.ac.uk/collection/C17/current/77SK/",
                                                "77SH": "http://vocab.nerc.ac.uk/collection/C17/current/77SH/",
                                                "77XV": "http://vocab.nerc.ac.uk/collection/C17/current/77XV/",
                                                "77ST": "http://vocab.nerc.ac.uk/collection/C17/current/77ST/",
                                                "77VS": "http://vocab.nerc.ac.uk/collection/C17/current/77VS/",
                                                "77WX": "http://vocab.nerc.ac.uk/collection/C17/current/77WX/",
                                                "774D": "http://vocab.nerc.ac.uk/collection/C17/current/774D/",
                                            }
    
                                            if value in mapping:
                                                emof_dict["measurementValueID"] = mapping[value]

                                        elif (
                                            param
                                            in [
                                                "Sampling laboratory accredited",
                                                "Analytical laboratory accredited",
                                            ]
                                            and value == "No"
                                        ):
                                            emof_dict["measurementValueID"] = (
                                                "http://vocab.nerc.ac.uk/collection/GBX/current/TX000020/"
                                            )

                                        elif (
                                            param
                                            in [
                                                "Sampling laboratory accredited",
                                                "Analytical laboratory accredited",
                                            ]
                                            and value == "Yes"
                                        ):
                                            emof_dict["measurementValueID"] = (
                                                "http://vocab.nerc.ac.uk/collection/GBX/current/TX000019/"
                                            )
                                        elif (
                                            param == "Observation point"
                                            and value == "Observation made from Airplane"
                                        ):
                                            emof_dict["measurementValueID"] = (
                                                "https://vocab.nerc.ac.uk/collection/L06/current/62/"
                                            )

                                        elif param == "Quality flag" and value in [
                                            "Blank",
                                            "E,",
                                            "S",
                                            "B",
                                            "<",
                                            ">",
                                            "R",
                                            "M",
                                            "Z",
                                        ]:
                                            emof_dict["measurementValueID"] = (
                                                "http://vocab.nerc.ac.uk/collection/L27/current/SMHI_QC/"
                                            )

                                        if emof_dict.get("measurementType", ""):
                                            self.dwca_measurementorfact.append(
                                                emof_dict.copy()
                                            )
            else:
                try:
                    # For checking for duplicates.
                    log_message = (
                        "Duplicates: "
                        + source_row.get("debug_info")
                        + " Key for param/unit: "
                        + str(emof_param_unit_id)
                    )
                    duplicate_row_number += 1
                    logger.error(log_message)
                    # if duplicate_row_number < 100:
                    #     logger.error(log_message)
                    # elif duplicate_row_number == 100:
                    #     logger.warning("MAX LIMIT OF 100 LOG ROWS.")
                except Exception as e:
                    logger.warning("eMoF: Exception-duplicates: " + str(e))
        # Finally.
        if duplicate_row_number > 0:
            logger.warning(
                "eMoF: Number of duplicates found: " + str(duplicate_row_number)
            )

    def add_content(self, content, source_row, result_dict):
        """ """
        translate_keys = self.translate.get_translate_from_dwc_keys()
        for term in content.get("dwcTerms", []):
            # print(term)
            # print(content["dwcTerms"][term])
            term_dict = content["dwcTerms"][term]
            if not term_dict:
                continue
            # Default.
            if "default" in term_dict:
                value = term_dict["default"]
                if value:
                    if term in translate_keys:
                        value = self.translate.get_translate_from_dwc(term, value)
                    result_dict[term] = value
            # Other alternatives, use first found.
            if "text" in term_dict:
                value = term_dict["text"]
                if value:
                    if term in translate_keys:
                        value = self.translate.get_translate_from_dwc(term, value)
                    result_dict[term] = value

            elif "sourceKey" in term_dict:
                source_key = term_dict["sourceKey"]
                value = source_row.get(source_key, "")
                if value:
                    if term in translate_keys:
                        value = self.translate.get_translate_from_dwc(term, value)
                    result_dict[term] = value

            elif "sourceKeyList" in term_dict:
                source_key_list = term_dict["sourceKeyList"]
                for source_key in source_key_list:
                    value = source_row.get(source_key, "")
                    if value:
                        if term in translate_keys:
                            value = self.translate.get_translate_from_dwc(term, value)
                        result_dict[term] = value
                        break

            elif "dwcaKey" in term_dict:
                dwca_key = term_dict["dwcaKey"]
                value = source_row.get(dwca_key, "")
                if value:
                    result_dict[term] = value

            elif "dynamic" in term_dict:
                dynamic_list = term_dict["dynamic"]
                dynamic_content_list = []
                for dynamic_item in dynamic_list:
                    if "dynamicKey" in dynamic_item:
                        dynamic_key = dynamic_item["dynamicKey"]
                        if "sourceKey" in dynamic_item:
                            source_key = dynamic_item["sourceKey"]
                            value = source_row.get(source_key, "")
                            if value:
                                if term in translate_keys:
                                    value = self.translate.get_translate_from_dwc(
                                        term, value
                                    )
                                content_string = dynamic_key + ": " + value
                                dynamic_content_list.append(content_string)
                        elif "sourceKeyList" in dynamic_item:
                            source_key_list = dynamic_item["sourceKeyList"]
                            for source_key in source_key_list:
                                value = source_row.get(source_key, "")
                                if value:
                                    if term in translate_keys:
                                        value = self.translate.get_translate_from_dwc(
                                            term, value
                                        )
                                    content_string = dynamic_key + ": " + value
                                    dynamic_content_list.append(content_string)
                                    break
                if dynamic_content_list:
                    result_dict[term] = ", ".join(dynamic_content_list)
        self.transform.transform_row(result_dict)

    # def extract_metadata(self):
    #     """ """
    #     latitude_min = 100.0
    #     latitude_max = -100.0
    #     longitude_min = 100.0
    #     longitude_max = -100.0
    #     sample_date_min = "9999-99-99"
    #     sample_date_max = "0000-00-00"

    #     param_unit_list = set()

    #     # Iterate over event rows.
    #     for event_row in self.dwca_event:
    #         # Don't check filtered rows.
    #         if event_row.get("remove_row", "") == "REMOVE":
    #             continue
    #         # Latitude/longitude.
    #         latitude = event_row.get("decimalLatitude", "100.0")
    #         longitude = event_row.get("decimalLongitude", "-100.0")
    #         try:
    #             latitude = float(latitude)
    #             longitude = float(longitude)
    #             if latitude != 100.0 and longitude != -100.0:
    #                 latitude_min = min(latitude_min, latitude)
    #                 latitude_max = max(latitude_max, latitude)
    #                 longitude_min = min(longitude_min, longitude)
    #                 longitude_max = max(longitude_max, longitude)
    #         except:
    #             # In case of BLANK, etc.
    #             pass
    #         # Sampling date.
    #         sample_date = event_row.get("eventDate", "")
    #         if sample_date != "":
    #             sample_date_min = min(sample_date_min, sample_date)
    #             sample_date_max = max(sample_date_max, sample_date)

    #     # Iterate over emof rows.
    #     for emof_row in self.dwca_measurementorfact:
    #         # Parameters and units.
    #         parameter = emof_row.get("measurementType", "")
    #         unit = emof_row.get("measurementUnit", "")
    #         param_unit = ""
    #         if parameter and unit:
    #             param_unit = parameter + " (" + unit + ")"
    #         elif parameter:
    #             param_unit = parameter
    #         if param_unit:
    #             param_unit_list.add(param_unit)

    #     # Done.
    #     self.latitude_min = ""
    #     self.latitude_max = ""
    #     self.longitude_min = ""
    #     self.longitude_max = ""
    #     self.sample_date_min = ""
    #     self.sample_date_max = ""

    #     if (
    #         latitude_min != 100.0
    #         and latitude_max != -100.0
    #         and longitude_min != 100.0
    #         and longitude_max != -100.0
    #     ):

    #         self.latitude_min = latitude_min
    #         self.latitude_max = latitude_max
    #         self.longitude_min = longitude_min
    #         self.longitude_max = longitude_max

    #     if sample_date_min != "9999-99-99" and sample_date_max != "0000-00-00":
    #         self.sample_date_min = sample_date_min
    #         self.sample_date_max = sample_date_max

    #     self.parameter_list = ", ".join(param_unit_list)

    # def add_metadata_to_eml(self, eml_content_rows):
    #     """ """
    #     self.eml_xml_rows = eml_content_rows
    #     if len(self.eml_xml_rows) > 1:
    #         for index, xml_row in enumerate(self.eml_xml_rows):
    #             if "REPLACE-" in xml_row:
    #                 self.eml_xml_rows[index] = self.eml_xml_rows[index].replace(
    #                     "REPLACE-packageId", "TODO-PACKAGE-ID"
    #                 )
    #                 self.eml_xml_rows[index] = self.eml_xml_rows[index].replace(
    #                     "REPLACE-dateStamp", str(datetime.datetime.today().date())
    #                 )
    #                 self.eml_xml_rows[index] = self.eml_xml_rows[index].replace(
    #                     "REPLACE-pubDate", str(datetime.datetime.today().date())
    #                 )
    #                 self.eml_xml_rows[index] = self.eml_xml_rows[index].replace(
    #                     "REPLACE-westLongitude", str(self.longitude_min)
    #                 )
    #                 self.eml_xml_rows[index] = self.eml_xml_rows[index].replace(
    #                     "REPLACE-eastLongitude", str(self.longitude_max)
    #                 )
    #                 self.eml_xml_rows[index] = self.eml_xml_rows[index].replace(
    #                     "REPLACE-northLatitude", str(self.latitude_max)
    #                 )
    #                 self.eml_xml_rows[index] = self.eml_xml_rows[index].replace(
    #                     "REPLACE-southLatitude", str(self.latitude_min)
    #                 )
    #                 self.eml_xml_rows[index] = self.eml_xml_rows[index].replace(
    #                     "REPLACE-beginDate", str(self.sample_date_min)
    #                 )
    #                 self.eml_xml_rows[index] = self.eml_xml_rows[index].replace(
    #                     "REPLACE-endDate", str(self.sample_date_max)
    #                 )
    #                 self.eml_xml_rows[index] = self.eml_xml_rows[index].replace(
    #                     "REPLACE-Parameters", str(self.parameter_list)
    #                 )

    #                 intellectual_rights = """
    #                     This work is licensed under the
    #                     <ulink url="https://creativecommons.org/publicdomain/zero/1.0/">
    #                         <citetitle>
    #                             CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
    #                         </citetitle>
    #                     </ulink>
    #                     license.
    #                     """
    #                 self.eml_xml_rows[index] = self.eml_xml_rows[index].replace(
    #                     "REPLACE-intellectualRights", intellectual_rights
    #                 )

    def create_meta_xml(self):
        """ """
        self.meta_xml_rows = []
        meta_xml = dwca_meta_xml.DarwinCoreMetaXml()
        self.meta_xml_rows = meta_xml.create_meta_xml(
            self.get_event_columns(),
            self.get_occurrence_columns(),
            self.get_measurementorfact_columns(),
        )

    def save_to_archive_file(self, metadata_eml):
        """ """
        # Darwin Core Archive parts.
        event_content = []
        occurrence_content = []
        measurementorfact_content = []

        # Append headers for Event, Occurrence and Measurementorfact.
        event_columns = self.get_event_columns()
        event_content.append("\t".join(event_columns))
        occurrence_content.append("\t".join(self.get_occurrence_columns()))
        measurementorfact_content.append("\t".join(self.get_measurementorfact_columns()))

        # Convert from dictionary to row for each item in the list.
        # Event.
        for row_dict in self.dwca_event:
            row = []
            for column_name in self.get_event_columns():
                check_value = row_dict.get(column_name, "")
                if check_value == "BLANK":
                    row.append("")
                else:
                    row.append(str(row_dict.get(column_name, "").strip()))
            event_content.append("\t".join(row))
        # Occurrence.
        for row_dict in self.dwca_occurrence:
            row = []
            for column_name in self.get_occurrence_columns():
                check_value = row_dict.get(column_name, "")
                if check_value == "BLANK":
                    row.append("")
                else:
                    row.append(str(row_dict.get(column_name, "").strip()))
            occurrence_content.append("\t".join(row))
        # Measurementorfact.
        for row_dict in self.dwca_measurementorfact:
            row = []
            for column_name in self.get_measurementorfact_columns():
                check_value = row_dict.get(column_name, "")
                if check_value == "BLANK":
                    row.append("")
                else:
                    row.append(str(row_dict.get(column_name, "").strip()))
            measurementorfact_content.append("\t".join(row))

        # Create zip archive.
        ziparchive = dwca_utils.ZipArchive(self.target_dwca_path)
        if len(event_content) > 1:
            ziparchive.appendZipEntry(
                "event.txt", ("\r\n".join(event_content).encode("utf-8"))
            )
        if len(occurrence_content) > 1:
            ziparchive.appendZipEntry(
                "occurrence.txt", ("\r\n".join(occurrence_content).encode("utf-8"))
            )
        if len(measurementorfact_content) > 1:
            ziparchive.appendZipEntry(
                "extendedmeasurementorfact.txt",
                ("\r\n".join(measurementorfact_content).encode("utf-8")),
            )

        if len(self.meta_xml_rows) > 1:
            ziparchive.appendZipEntry(
                "meta.xml", ("\r\n".join(self.meta_xml_rows).encode("utf-8"))
            )

        # Add eml.xml files to zip.
        if len(metadata_eml.metadata_eml_rows) > 1:
            #
            eml_document = "\r\n".join(metadata_eml.metadata_eml_rows).encode("utf-8")
            # eml_document = self.eml_xml_rows.encode("utf-8")
            ziparchive.appendZipEntry("eml.xml", eml_document)

    def get_event_columns(self):
        """Implementation of abstract method declared in DwcDatatypeBase."""
        event_columns = self.dwca_gen_config.field_mapping.get("dwcaEventColumns", [])
        return event_columns

    def get_occurrence_columns(self):
        """Implementation of abstract method declared in DwcDatatypeBase."""
        occurrence_columns = self.dwca_gen_config.field_mapping.get(
            "dwcaOccurrenceColumns", []
        )
        return occurrence_columns

    def get_measurementorfact_columns(self):
        """Implementation of abstract method declared in DwcDatatypeBase."""
        emof_columns = self.dwca_gen_config.field_mapping.get("dwcaEmofColumns", [])
        return emof_columns


def _read_aphia_id_mapping() -> dict[str, str]:
    aphipa_id_file_path = darwincore.DATA_IN_PATH / "resources/add_aphia_id_taxon.txt"
    with aphipa_id_file_path.open() as aphia_id_file:
        additional_aphia_id = {
            row["scientific_name"]: row["AphiaID"]
            for row in csv.DictReader(aphia_id_file, delimiter="\t")
        }
    return additional_aphia_id
