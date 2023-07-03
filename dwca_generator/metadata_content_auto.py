#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2022-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import logging
import datetime

import dwca_generator

class MetadataContentAuto(object):
    """ """

    def __init__(self):
        """ """

    def extract_metadata(self, dwca_event, dwca_measurementorfact):
        """ """
        self.dwca_event = dwca_event
        self.dwca_measurementorfact = dwca_measurementorfact
        latitude_min = 100.0
        latitude_max = -100.0
        longitude_min = 100.0
        longitude_max = -100.0
        sample_date_min = "9999-99-99"
        sample_date_max = "0000-00-00"
        param_unit_list = set()

        self.revision_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')

        # Iterate over event rows.
        for event_row in self.dwca_event:
            # Don't check filtered rows.
            if event_row.get("remove_row", "") == "REMOVE":
                continue
            # Latitude/longitude.
            latitude = event_row.get("decimalLatitude", "100.0")
            longitude = event_row.get("decimalLongitude", "-100.0")
            try:
                latitude = float(latitude)
                longitude = float(longitude)
                if latitude != 100.0 and longitude != -100.0:
                    latitude_min = min(latitude_min, latitude)
                    latitude_max = max(latitude_max, latitude)
                    longitude_min = min(longitude_min, longitude)
                    longitude_max = max(longitude_max, longitude)
            except:
                # In case of BLANK, etc.
                pass
            # Sampling date.
            sample_date = event_row.get("eventDate", "")
            if sample_date != "":
                sample_date_min = min(sample_date_min, sample_date)
                sample_date_max = max(sample_date_max, sample_date)

        # Iterate over emof rows.
        for emof_row in self.dwca_measurementorfact:
            # Parameters and units.
            parameter = emof_row.get("measurementType", "")
            unit = emof_row.get("measurementUnit", "")
            param_unit = ""
            if parameter and unit:
                param_unit = parameter + " (" + unit + ")"
            elif parameter:
                param_unit = parameter
            if param_unit:
                param_unit_list.add(param_unit)

        # Done.
        self.latitude_min = ""
        self.latitude_max = ""
        self.longitude_min = ""
        self.longitude_max = ""
        self.sample_date_min = ""
        self.sample_date_max = ""

        if (
            latitude_min != 100.0
            and latitude_max != -100.0
            and longitude_min != 100.0
            and longitude_max != -100.0
        ):

            self.latitude_min = latitude_min
            self.latitude_max = latitude_max
            self.longitude_min = longitude_min
            self.longitude_max = longitude_max

        if sample_date_min != "9999-99-99" and sample_date_max != "0000-00-00":
            self.sample_date_min = sample_date_min
            self.sample_date_max = sample_date_max

        self.parameter_list = ", ".join(param_unit_list)
