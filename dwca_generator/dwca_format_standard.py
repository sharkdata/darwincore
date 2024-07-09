#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import logging
import datetime

import dwca_generator
#import pandas as pd

class DwcaFormatStandard(object):
    """ """

    def __init__(self, data, dwca_gen_config, worms_info, translate):
        """ Darwin Core Archive Format base class. """

        self.target_dwca_path = pathlib.Path(dwca_gen_config.dwca_target)
        self.data_object = data
        self.dwca_gen_config = dwca_gen_config
        self.worms_info_object = worms_info
        self.translate = translate
       #
        self.clear()
        #
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
            event_control_dict[dwca_node_name][
                "used_key_list"
            ] = set()  # To avoid duplicates.
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
                    event_dict["type"] = dwca_node_name
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

                        # Check if sampleSizeValue is empty and if so make sampleSizeUnit empty too
                    if not event_dict.get("sampleSizeValue"):
                       event_dict["sampleSizeUnit"] = ""

                        # Seal Pathology area fix using obis.org/maptool moving position from county capital to position in water and with individual uncertainty radius m
                    if event_dict.get("verbatimLocality") == "BD" and "SHARK_SealPathology" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "BD Norrbotten County"
                        event_dict["latitude"] = "65.45"
                        event_dict["decimalLongitude"] = "22.93"
                        event_dict["coordinateUncertaintyInMeters"] = "85550"

                    if event_dict.get("verbatimLocality") == "AC" and "SHARK_SealPathology" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "AC Västerbotten County"
                        event_dict["decimalLatitude"] = "63.97"
                        event_dict["decimalLongitude"] = "20.94"
                        event_dict["coordinateUncertaintyInMeters"] = "134320"

                    if event_dict.get("verbatimLocality") == "Y" and "SHARK_SealPathology" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "Y Västernorrland County"
                        event_dict["decimalLatitude"] = "62.78"
                        event_dict["decimalLongitude"] = "18.40"
                        event_dict["coordinateUncertaintyInMeters"] = "103490"

                    if event_dict.get("verbatimLocality") in ["X", "x"] and "SHARK_SealPathology" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "X Gävleborg County"
                        event_dict["decimalLatitude"] = "61.37"
                        event_dict["decimalLongitude"] = "17.36"
                        event_dict["coordinateUncertaintyInMeters"] = "104510"

                    if event_dict.get("verbatimLocality") == "C" and "SHARK_SealPathology" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "C Uppsala County"
                        event_dict["decimalLatitude"] = "60.52"
                        event_dict["decimalLongitude"] = "18.20"
                        event_dict["coordinateUncertaintyInMeters"] = "69370"

                    if event_dict.get("verbatimLocality") == "AB" and "SHARK_SealPathology" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "AB Stockholm County"
                        event_dict["decimalLatitude"] = "59.31"
                        event_dict["decimalLongitude"] = "18.91"
                        event_dict["coordinateUncertaintyInMeters"] = "141270"

                    if event_dict.get("verbatimLocality") == "D" and "SHARK_SealPathology" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "D Södermanland County"
                        event_dict["decimalLatitude"] = "58.70"
                        event_dict["decimalLongitude"] = "17.38"
                        event_dict["coordinateUncertaintyInMeters"] = "48200"

                    if event_dict.get("verbatimLocality") == "E" and "SHARK_SealPathology" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "E Östergötland County"
                        event_dict["decimalLatitude"] = "58.32"
                        event_dict["decimalLongitude"] = "17.02"
                        event_dict["coordinateUncertaintyInMeters"] = "65330"

                    if event_dict.get("verbatimLocality") == "H" and "SHARK_SealPathology" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "H Kalmar County"
                        event_dict["decimalLatitude"] = "56.95"
                        event_dict["decimalLongitude"] = "16.56"
                        event_dict["coordinateUncertaintyInMeters"] = "138750"

                    if event_dict.get("verbatimLocality") == "I" and "SHARK_SealPathology" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "I Gotland County"
                        event_dict["decimalLatitude"] = "57.64"
                        event_dict["decimalLongitude"] = "18.84"
                        event_dict["coordinateUncertaintyInMeters"] = "121390"

                    if event_dict.get("verbatimLocality") == "K" and "SHARK_SealPathology" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "K Blekinge County"
                        event_dict["decimalLatitude"] = "56.02"
                        event_dict["decimalLongitude"] = "15.40"
                        event_dict["coordinateUncertaintyInMeters"] = "64370"

                    if event_dict.get("verbatimLocality") == "M" and "SHARK_SealPathology" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "M Skåne County"
                        event_dict["decimalLatitude"] = "55.67"
                        event_dict["decimalLongitude"] = "12.99"
                        event_dict["coordinateUncertaintyInMeters"] = "122710"

                    if event_dict.get("verbatimLocality") == "N" and "SHARK_SealPathology" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "N Halland County"
                        event_dict["decimalLatitude"] = "56.99"
                        event_dict["decimalLongitude"] = "12.20"
                        event_dict["coordinateUncertaintyInMeters"] = "84390"

                    if event_dict.get("verbatimLocality") == "O" and "SHARK_SealPathology" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "O Västra Götaland County"
                        event_dict["decimalLatitude"] = "58.25"
                        event_dict["decimalLongitude"] = "11.31"
                        event_dict["coordinateUncertaintyInMeters"] = "107450"

                    #Greyseal fix fix using obis.org/maptool moving position from county capital to position in water and with individual uncertainty radius m

                    if event_dict.get("decimalLatitude") == "58.40333" and event_dict.get("decimalLongitude") == "15.62167" and "SHARK_GreySeal" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "E Östergötland County"
                        event_dict["decimalLatitude"] = "58.32"
                        event_dict["decimalLongitude"] = "17.02"
                        event_dict["coordinateUncertaintyInMeters"] = "65330"

                    if event_dict.get("decimalLatitude") == "58.76167" and event_dict.get("decimalLongitude") == "17.02333" and "SHARK_GreySeal" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "D Södermanland County"
                        event_dict["decimalLatitude"] = "58.70"
                        event_dict["decimalLongitude"] = "17.38"
                        event_dict["coordinateUncertaintyInMeters"] = "48200"

                    if event_dict.get("decimalLatitude") == "59.33833" and event_dict.get("decimalLongitude") == "18.01667" and "SHARK_GreySeal" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "AB Stockholm County"
                        event_dict["decimalLatitude"] = "59.31"
                        event_dict["decimalLongitude"] = "18.91"
                        event_dict["coordinateUncertaintyInMeters"] = "141270"

                    if event_dict.get("decimalLatitude") == "59.85833" and event_dict.get("decimalLongitude") == "17.64500" and "SHARK_GreySeal" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "C Uppsala County"
                        event_dict["decimalLatitude"] = "60.52"
                        event_dict["decimalLongitude"] = "18.20"
                        event_dict["coordinateUncertaintyInMeters"] = "69370"

                    if event_dict.get("decimalLatitude") == "60.67500" and event_dict.get("decimalLongitude") == "17.15000" and "SHARK_GreySeal" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "X Gävleborg County"
                        event_dict["decimalLatitude"] = "61.37"
                        event_dict["decimalLongitude"] = "17.36"
                        event_dict["coordinateUncertaintyInMeters"] = "104510"

                    if event_dict.get("decimalLatitude") == "62.63000" and event_dict.get("decimalLongitude") == "17.93667" and "SHARK_GreySeal" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "Y Västernorrland County"
                        event_dict["decimalLatitude"] = "62.78"
                        event_dict["decimalLongitude"] = "18.40"
                        event_dict["coordinateUncertaintyInMeters"] = "103490"

                    if event_dict.get("decimalLatitude") == "63.83167" and event_dict.get("decimalLongitude") == "20.26667" and "SHARK_GreySeal" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "AC Västerbotten County"
                        event_dict["decimalLatitude"] = "63.97"
                        event_dict["decimalLongitude"] = "20.94"
                        event_dict["coordinateUncertaintyInMeters"] = "134320"

                    if event_dict.get("decimalLatitude") == "65.58333" and event_dict.get("decimalLongitude") == "22.16333" and "SHARK_GreySeal" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "BD Norrbotten County"
                        event_dict["latitude"] = "65.45"
                        event_dict["decimalLongitude"] = "22.93"
                        event_dict["coordinateUncertaintyInMeters"] = "85550"

                    if event_dict.get("decimalLatitude") == "57.64167" and event_dict.get("decimalLongitude") == "18.29667" and "SHARK_GreySeal" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "I Gotland County"
                        event_dict["decimalLatitude"] = "57.64"
                        event_dict["decimalLongitude"] = "18.84"
                        event_dict["coordinateUncertaintyInMeters"] = "121390"

                    if event_dict.get("decimalLatitude") == "56.66167" and event_dict.get("decimalLongitude") == "16.36000" and "SHARK_GreySeal" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "H Kalmar County"
                        event_dict["decimalLatitude"] = "56.95"
                        event_dict["decimalLongitude"] = "16.56"
                        event_dict["coordinateUncertaintyInMeters"] = "138750"

                    if event_dict.get("decimalLatitude") == "56.20000" and event_dict.get("decimalLongitude") == "15.95000" and "SHARK_GreySeal" in event_dict.get("dynamicProperties") or event_dict.get("decimalLatitude") == "56.16667" and event_dict.get("decimalLongitude") == "15.58500" and "SHARK_GreySeal" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "K Blekinge County"
                        event_dict["decimalLatitude"] = "56.02"
                        event_dict["decimalLongitude"] = "15.40"
                        event_dict["coordinateUncertaintyInMeters"] = "64370"

                    if event_dict.get("decimalLatitude") == "55.40000" and event_dict.get("decimalLongitude") == "12.91667" and "SHARK_GreySeal" in event_dict.get("dynamicProperties"):
                        event_dict["locality"] = "M Skåne County"
                        event_dict["decimalLatitude"] = "55.67"
                        event_dict["decimalLongitude"] = "12.99"
                        event_dict["coordinateUncertaintyInMeters"] = "122710"

        
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
            occurrence_control_dict[dwca_node_name][
                "used_key_list"
            ] = set()  # To avoid duplicates.
            occurrence_control_dict[dwca_node_name]["dwc_key_name"] = occurrence_keys[
                index
            ]["keyName"]

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
                        worms_info_dict = self.worms_info_object.get_worms_info(
                            aphia_id, scientific_name
                        )
                        source_row.update(worms_info_dict)

                        # Create LSID for Phytoplankton BVOL data.
                        bvol_aphia_id = source_row.get("bvol_aphia_id", "")
                        if bvol_aphia_id:
                            bvol_aphia_lsid = "https://www.marinespecies.org/aphia.php?p=taxdetails&id=" + bvol_aphia_id
                            source_row["bvol_aphia_lsid"] = bvol_aphia_lsid


                        # Add content.
                        self.add_content(content, source_row, occurrence_dict)
                        
                        # Add missing AphiaID for phytoplankton (because not in NOMP-bvol list)
                        if "SHARK_Phytoplankton" in occurrence_dict.get("dynamicProperties") and occurrence_dict.get("scientificNameID", "") == "":
                            dict_missing = {}
                            with open("C:/Python/DV_export/darwincore/data_in/resources/add_aphia_id_phytoplankton.txt") as f:
                                for line in f:
                                  (key, val) = line.split("\t")
                                  dict_missing[key] = val
                            for missing_taxa_id, ID in dict_missing.items():
                                if occurrence_dict.get("scientificName","") == missing_taxa_id:
                                  occurrence_dict["scientificNameID"] = ID
                        
                       # Phytoplankton fix
                        if all(
                            key in occurrence_dict and "SHARK_Phytoplankton" in occurrence_dict.get("dynamicProperties", "")
                            for key in ("dynamicProperties", "scientificName", "verbatimIdentification", "scientificNameID")
                        ) and occurrence_dict.get("scientificName") == "Bacillariophyceae" and occurrence_dict.get("verbatimIdentification") == "Pennales" and "1304629" in occurrence_dict.get("scientificNameID", ""):
                            occurrence_dict["scientificName"] = "Pennales"

                        # Add URI path for Aphia-id if numeric.
                        worms_lsid = occurrence_dict.get("scientificNameID", "")
                        # print("DEBUG 1", worms_lsid)
                        try:
                            worms_lsid_int = int(worms_lsid)
                            worms_lsid_new = (
                                "urn:lsid:marinespecies.org:taxname:" + worms_lsid
                            )
                            occurrence_dict["scientificNameID"] = worms_lsid_new
                            # print("DEBUG 2", worms_lsid_new)
                        except:
                            pass

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
                            parameter = emof_dict.get("measurementType", "")
                            unit = emof_dict.get("measurementUnit", "")

                            if parameter == "# counted":
                                emof_dict["measurementType"] = "Count"
                                emof_dict["measurementTypeID"] = "http://vocab.nerc.ac.uk/collection/P01/current/OCOUNT01/"

                            elif parameter == "Abundance":
                                emof_dict["measurementTypeID"] = "http://vocab.nerc.ac.uk/collection/P01/current/SDBIOL01"

                            elif parameter == "Carbon content":
                                emof_dict["measurementTypeID"] = "http://vocab.nerc.ac.uk/collection/P01/current/MDMAP010/"

                            elif parameter == "Length mean":
                                emof_dict["measurementTypeID"] = "http://vocab.nerc.ac.uk/collection/P01/current/OBSINDLX/"

                            elif parameter == "Length":
                                emof_dict["measurementTypeID"] = "http://vocab.nerc.ac.uk/collection/P01/current/OBSINDLX/"

                            elif parameter == "Wet weight":
                                emof_dict["measurementTypeID"] = "http://vocab.nerc.ac.uk/collection/P01/current/OWETBM01"

                            elif parameter == "Wet weight per volume":
                                emof_dict["measurementTypeID"] = "http://vocab.nerc.ac.uk/collection/P01/current/SDBIOL04"

                            elif parameter == "Wet weight/volume":
                                emof_dict["measurementType"] = "Wet weight per volume"
                                emof_dict["measurementTypeID"] = "http://vocab.nerc.ac.uk/collection/P01/current/SDBIOL04"

                            elif parameter == "Cover":
                                emof_dict["measurementTypeID"] = "http://vocab.nerc.ac.uk/collection/P01/current/PCOV7736/"

                            elif parameter == "Dry weight":
                                emof_dict["measurementTypeID"] = "http://vocab.nerc.ac.uk/collection/P01/current/SPDWXX01/"

                            elif parameter == "Salinity":
                                emof_dict["measurementTypeID"] = "http://vocab.nerc.ac.uk/collection/P01/current/PSLTZZ01/"

                            elif parameter == "Temperature":
                                emof_dict["measurementTypeID"] = "http://vocab.nerc.ac.uk/collection/P01/current/TEMPPR01/"

                            elif parameter == "Air temperature":
                                emof_dict["measurementTypeID"] = "http://vocab.nerc.ac.uk/collection/OD1/current/AIRTEMP/"

                            elif parameter == "Air pressure":
                                emof_dict["measurementTypeID"] = "http://vocab.nerc.ac.uk/collection/P02/current/CAPH/"

                            elif parameter == "Wet weight/area":
                                emof_dict["measurementType"] = "Wet weight per area"

                            elif parameter == "Cell volume":
                                emof_dict["measurementTypeID"] = "http://vocab.nerc.ac.uk/collection/P01/current/CVOLZZ01/"

                            elif parameter == "Biovolume concentration":
                                emof_dict["measurementTypeID"] = "http://vocab.nerc.ac.uk/collection/P01/current/CVOLUKNB/"


                            #nerc codes found at https://vocab.nerc.ac.uk/collection/P06/current/

                            if unit == "um":
                                emof_dict["measurementUnit"] = "Micrometres"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UMIC/"

                            elif unit == "mm":
                                emof_dict["measurementUnit"] = "Millimetres"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UXMM/"

                            elif unit == "m":
                                emof_dict["measurementUnit"] = "Metres"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/ULAA/"

                            elif unit == "g":
                                emof_dict["measurementUnit"] = "Grams"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UGRM/"

                            elif unit == "L":
                                emof_dict["measurementUnit"] = "Litres"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/ULIT/"

                            elif unit == "m/s":
                                emof_dict["measurementUnit"] = "Metres per second"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UVAA/"

                            elif unit == "ml":
                                emof_dict["measurementUnit"] = "Millilitres"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/VVML/"

                            elif unit == "cm2":
                                emof_dict["measurementUnit"] = "Square centimetres"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/SQCM/"

                            elif unit == "cm3":
                                emof_dict["measurementUnit"] = "Cubic centimetres"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/VVCC/"

                            elif unit == "h":
                                emof_dict["measurementUnit"] = "Hours"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UHOR/"

                            elif unit == "hpa":
                                emof_dict["measurementUnit"] = "Hectopascals"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/HPAX/"

                            elif unit == "mm3/l":
                                emof_dict["measurementUnit"] = "Cubic millimetres per litre"

                            elif unit == "g/m3":
                                emof_dict["measurementUnit"] = "Grams per cubic metre"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UGMC/"

                            elif unit == "ugC/l":
                                emof_dict["measurementUnit"] = "Micrograms per litre"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UGPL/"

                            elif unit == "um3":
                                emof_dict["measurementUnit"] = "Cubic micrometres"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UMCU/"

                            elif unit == "ind/l":
                                emof_dict["measurementUnit"] = "Individual per litre"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UCPL/"

                            elif unit == "ind/m3":
                                emof_dict["measurementUnit"] = "Individual per cubic metre"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UPMM/"

                            elif unit == "ind/m2":
                                emof_dict["measurementUnit"] = "Individual per square metre"

                            elif unit == "ug/m3":
                                emof_dict["measurementUnit"] = "Micrograms per cubic metre"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/MCUG/"

                            elif unit == "deg":
                                emof_dict["measurementUnit"] = "Degrees"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UAAA/"

                            elif unit == "degC":
                                emof_dict["measurementUnit"] = "Degrees Celsius"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UPAA/"

                            elif unit == "C":
                                emof_dict["measurementUnit"] = "Degrees Celsius"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UPAA/"

                            elif unit == "cells/l":
                                emof_dict["measurementUnit"] = "Cell per litre"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UCPL/"

                            elif unit == "ind/analysed sample fraction":
                                emof_dict["measurementUnit"] = "Individual per analysed sample fraction"

                            elif unit == "nr":
                                emof_dict["measurementUnit"] = "Number"

                            elif unit == "Detection minutes/day":
                                emof_dict["measurementUnit"] = "Minutes per day"

                            elif unit == "%":
                                emof_dict["measurementUnit"] = "Percent"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UPCT/"

                            elif unit == "mg/m2":
                                emof_dict["measurementUnit"] = "Milligrams per square metre"

                            elif unit == "mg/m3":
                                emof_dict["measurementUnit"] = "Milligrams per cubic metre"

                            elif unit == "ind": #measurementType Count with ind as unit in SHARK
                                emof_dict["measurementUnit"] = "Dimensionless"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UUUU/"


                            if parameter == "Salinity" and unit == "":
                                emof_dict["measurementUnit"] = "Dimensionless"
                                emof_dict["measurementUnitID"] = "http://vocab.nerc.ac.uk/collection/P06/current/UUUU/"


                            self.dwca_measurementorfact.append(emof_dict.copy())

                        # Get key.
                        event_node_key = source_row.get(
                            control_dict["dwc_key_name"], ""
                        )
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
                                    if 'text' in extraMeasurement.keys():
                                        value = extraMeasurement.get("text","")
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

                                        if emof_dict.get("measurementType", ""):
                                            self.dwca_measurementorfact.append(
                                                emof_dict.copy()
                                            )
            else:
                try:
                    # For checking for duplicates.
                    log_message = (
                        "Duplicates: "
                        + source_row.get("debug_info" "")
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
    #                         <citetitle>CC0 1.0 Universal (CC0 1.0) Public Domain Dedication</citetitle>
    #                     </ulink>
    #                     license.
    #                     """
    #                 self.eml_xml_rows[index] = self.eml_xml_rows[index].replace(
    #                     "REPLACE-intellectualRights", intellectual_rights
    #                 )

    def create_meta_xml(self):
        """ """
        self.meta_xml_rows = []
        meta_xml = dwca_generator.DarwinCoreMetaXml()
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
        measurementorfact_content.append(
            "\t".join(self.get_measurementorfact_columns())
        )

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
        ziparchive = dwca_generator.ZipArchive(self.target_dwca_path)
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
        """ Implementation of abstract method declared in DwcDatatypeBase. """
        event_columns = self.dwca_gen_config.field_mapping.get("dwcaEventColumns", [])
        return event_columns

    def get_occurrence_columns(self):
        """ Implementation of abstract method declared in DwcDatatypeBase. """
        occurrence_columns = self.dwca_gen_config.field_mapping.get(
            "dwcaOccurrenceColumns", []
        )
        return occurrence_columns

    def get_measurementorfact_columns(self):
        """ Implementation of abstract method declared in DwcDatatypeBase. """
        emof_columns = self.dwca_gen_config.field_mapping.get("dwcaEmofColumns", [])
        return emof_columns
