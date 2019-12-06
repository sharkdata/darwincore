#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import openpyxl

class DwcaLocations():
    """ """
    def __init__(self):
        """ """
#         self.translate_taxa_dict = {}
#         self.missing_taxa_list = []
#      
#     def get_translated_aphiaid_and_name(self, scientific_name):
#         """ """
#         if scientific_name in self.translate_taxa_dict:
#             return self.translate_taxa_dict[scientific_name]
#         #
#         if scientific_name not in self.missing_taxa_list:
#             self.missing_taxa_list.append(scientific_name)
#         #    
# #         return ('', '')
#         return {}
#      
#     def get_missing_taxa_list(self):
#         """ """
#         return self.missing_taxa_list
#      
#     def load_translate_taxa(self, taxa_file_path):
#         """ """
#         self.translate_taxa_dict = {}
#         self.missing_taxa_list = []
#         #
#         translate_file_path = pathlib.Path(taxa_file_path)
#         
#         with translate_file_path.open('r') as translate_file:
#             for index, row in enumerate(translate_file):
#                 row = [item.strip() for item in row.split('\t')]
#                 if index == 0:
#                     # dyntaxa_scientific_name    worms_valid_aphia_id    worms_valid_name
#                     header = row
#                 else:
#                     if len(row) >= 2:
#                         row_dict = dict(zip(header, row))
#                         self.translate_taxa_dict[row_dict.get('scientific_name', '')] = row_dict
