#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2022-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import datetime


class MetadataDwcaEml(object):
    """ """

    def __init__(self):
        """ """
        self.metadata_eml_rows = []

    def add_metadata_to_eml(self, eml_content_rows, metadata_content):
        """ """
        self.metadata_eml_rows = eml_content_rows
        if len(self.metadata_eml_rows) > 1:
            for index, xml_row in enumerate(self.metadata_eml_rows):
                if "REPLACE-" in xml_row:
                    self.metadata_eml_rows[index] = self.metadata_eml_rows[index].replace(
                        "REPLACE-packageId", "TODO-PACKAGE-ID"
                    )
                    self.metadata_eml_rows[index] = self.metadata_eml_rows[index].replace(
                        "REPLACE-dateStamp", str(datetime.datetime.today().date())
                    )
                    self.metadata_eml_rows[index] = self.metadata_eml_rows[index].replace(
                        "REPLACE-pubDate", str(datetime.datetime.today().date())
                    )
                    self.metadata_eml_rows[index] = self.metadata_eml_rows[index].replace(
                        "REPLACE-westLongitude", str(metadata_content.longitude_min)
                    )
                    self.metadata_eml_rows[index] = self.metadata_eml_rows[index].replace(
                        "REPLACE-eastLongitude", str(metadata_content.longitude_max)
                    )
                    self.metadata_eml_rows[index] = self.metadata_eml_rows[index].replace(
                        "REPLACE-northLatitude", str(metadata_content.latitude_max)
                    )
                    self.metadata_eml_rows[index] = self.metadata_eml_rows[index].replace(
                        "REPLACE-southLatitude", str(metadata_content.latitude_min)
                    )
                    self.metadata_eml_rows[index] = self.metadata_eml_rows[index].replace(
                        "REPLACE-beginDate", str(metadata_content.sample_date_min)
                    )
                    self.metadata_eml_rows[index] = self.metadata_eml_rows[index].replace(
                        "REPLACE-endDate", str(metadata_content.sample_date_max)
                    )
                    self.metadata_eml_rows[index] = self.metadata_eml_rows[index].replace(
                        "REPLACE-Parameters", str(metadata_content.parameter_list)
                    )

                    intellectual_rights = """
                        This work is licensed under the
                        <ulink url="https://creativecommons.org/publicdomain/zero/1.0/">
                            <citetitle>
                                CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
                            </citetitle>
                        </ulink>
                        license.
                        """
                    self.metadata_eml_rows[index] = self.metadata_eml_rows[index].replace(
                        "REPLACE-intellectualRights", intellectual_rights
                    )
