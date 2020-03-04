#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019-present SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib

class DwcaSpeciesWorms():
    """ Used to translate from the Swedish taxonomic list, DynTaxa, to 
        the internationally used WoRMS list ( http://marinespecies.org ).
        The resource file also contains additional taxonomic information
        from the WoRMS database.
    """
    def __init__(self, taxa_file_path):
        """ """
        self.taxa_file_path = taxa_file_path
        self.clear()
        self.load_translate_taxa()
    
    def clear(self):
        """ """
        # Dictionary with scientific_name as key and a dictionary with
        # taxonomic info as value.
        # The key is mainly taxa from DynTaxa, but Worms taxa are also
        # added if they differ.
        self.translate_taxa_dict = {}
        # Store missing taxa for later use.
        self.missing_taxa_list = []
        # To make it faster to get taxonomic info.
        self.info_lookup_dict = {}
    
    def get_translated_aphiaid_and_name(self, scientific_name):
        """ Returns a dictionary containing taxonomical information. """
        if scientific_name in self.translate_taxa_dict:
            return self.translate_taxa_dict[scientific_name]
        # Store missing taxa.
        if scientific_name not in self.missing_taxa_list:
            self.missing_taxa_list.append(scientific_name)
        # No found.
        return {}
     
    def get_info_as_dwc_dict(self, scientific_name='', source_dict={}):
        """ Adds taxonomic info to the result dictionary, 
            or creates a new empty one. 
        """
        result_dict={}
        # Check the source_dict if not attached.
        if not scientific_name:
            scientific_name = source_dict.get('scientific_name', '')
        if not scientific_name:
            scientific_name = source_dict.get('reported_scientific_name', '')
        if not scientific_name:
            scientific_name = source_dict.get('scientificName', '')
        #
        if scientific_name:
            if scientific_name in self.info_lookup_dict:
                return self.info_lookup_dict[scientific_name]
            else:
                taxa_dict = self.get_translated_aphiaid_and_name(scientific_name)
                self.info_lookup_dict[scientific_name] = result_dict
                # Link to DynTaxa.
                dyntaxa_id = taxa_dict.get('dyntaxa_id', '')
                if dyntaxa_id:
                    result_dict['taxonID'] = 'urn:lsid:dyntaxa.se:Taxon:' + dyntaxa_id
                else:
                    result_dict['taxonID'] = ''
                # From WoRMS.
                result_dict['scientificNameID'] = taxa_dict.get('worms_lsid', '')
                result_dict['scientificName'] = taxa_dict.get('worms_scientific_name', '')
                result_dict['scientificNameAuthorship'] = taxa_dict.get('worms_authority', '')
                result_dict['taxonRank'] = taxa_dict.get('worms_rank', '')
                result_dict['kingdom'] = taxa_dict.get('worms_kingdom', '')
                result_dict['phylum'] = taxa_dict.get('worms_phylum', '')
                result_dict['class'] = taxa_dict.get('worms_class', '')
                result_dict['order'] = taxa_dict.get('worms_order', '')
                result_dict['family'] = taxa_dict.get('worms_family', '')
                result_dict['genus'] = taxa_dict.get('worms_genus', '')
        #
        return result_dict
    
    def get_missing_taxa_list(self):
        """ """
        return self.missing_taxa_list
     
    def load_translate_taxa(self):
        """ """
        self.translate_taxa_dict = {}
        self.missing_taxa_list = []
        #
        translate_file_path = pathlib.Path(self.taxa_file_path)
        
        if translate_file_path.suffix in ['.txt', '.tsv']:
            # Stored as text file.
            with translate_file_path.open('r') as translate_file:
                for index, row in enumerate(translate_file):
                    row = [item.strip() for item in row.split('\t')]
                    if index == 0:
                        # dyntaxa_scientific_name    worms_valid_aphia_id    worms_valid_name
                        header = row
                    else:
                        if len(row) >= 2:
                            row_dict = dict(zip(header, row))
                            scientific_name = row_dict.get('scientific_name', '')
                            worms_scientific_name = row_dict.get('worms_scientific_name', '')
                            self.translate_taxa_dict[scientific_name] = row_dict
                            if scientific_name != worms_scientific_name:
                                self.translate_taxa_dict[worms_scientific_name] = row_dict
        
#         elif translate_file_path.suffix in ['.xlsx']:
#             # Stored as Excel file.
#             # TODO: Excel.
        

