#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib


class TaxaWorms:
    """Used for additional taxonomic information from
    the WoRMS database: http://marinespecies.org"""

    def __init__(self, taxa_file_path):
        """ """
        self.taxa_file_path = taxa_file_path
        self.clear()
        self.load_taxa_worms()

    def clear(self):
        """ """
        # Dictionary with AphiaID as key and a dictionary with
        # taxonomic info as value.
        self.taxa_worms_dict = {}
        # Store missing taxa for later use.
        self.missing_taxa_set = set()

    def get_worms_info(self, aphia_id="", scientific_name=""):
        """ """
        taxa_dict = {}
        if (aphia_id != "") and (aphia_id in self.taxa_worms_dict):
            taxa_dict = self.taxa_worms_dict[aphia_id]
        else:
            if aphia_id == "":
                aphia_id = "Empty"
            missing_info_str = scientific_name + " AphiaID: " + str(aphia_id)
            self.missing_taxa_set.add(missing_info_str)
        #
        return taxa_dict

    def get_missing_taxa_list(self):
        """ """
        return sorted(list(self.missing_taxa_set))

    def load_taxa_worms(self):
        """ """
        self.clear()
        #
        translate_file_path = pathlib.Path(self.taxa_file_path)

        if translate_file_path.suffix in [".txt", ".tsv"]:
            # Stored as text file.
            header = []
            with translate_file_path.open("r", encoding="utf8") as translate_file:
                for index, row in enumerate(translate_file):
                    row = [item.strip() for item in row.split("\t")]
                    if index == 0:
                        header = row
                    elif len(row) >= 2:
                        row_dict = dict(zip(header, row))
                        aphia_id = str(row_dict.get("aphia_id", ""))
                        info_dict = {}
                        info_dict["aphia_id"] = aphia_id
                        info_dict["worms_scientific_name"] = row_dict.get(
                            "scientific_name", ""
                        )
                        info_dict["worms_authority"] = row_dict.get("authority", "")
                        info_dict["worms_rank"] = row_dict.get("rank", "")
                        info_dict["worms_url"] = row_dict.get("url", "")
                        info_dict["worms_status"] = row_dict.get("status", "")
                        info_dict["worms_valid_aphia_id"] = row_dict.get(
                            "valid_aphia_id", ""
                        )
                        info_dict["worms_valid_name"] = row_dict.get("valid_name", "")
                        info_dict["worms_valid_authority"] = row_dict.get(
                            "valid_authority", ""
                        )
                        info_dict["worms_kingdom"] = row_dict.get("kingdom", "")
                        info_dict["worms_kingdom"] = row_dict.get("kingdom", "")
                        info_dict["worms_kingdom"] = row_dict.get("kingdom", "")
                        info_dict["worms_phylum"] = row_dict.get("phylum", "")
                        info_dict["worms_class"] = row_dict.get("class", "")
                        info_dict["worms_order"] = row_dict.get("order", "")
                        info_dict["worms_family"] = row_dict.get("family", "")
                        info_dict["worms_genus"] = row_dict.get("genus", "")
                        info_dict["worms_classification"] = row_dict.get(
                            "classification", ""
                        )
                        info_dict["lsid"] = row_dict.get(
                            "lsid", ""
                        )  ## MH lägger till LSID
                        self.taxa_worms_dict[aphia_id] = info_dict
