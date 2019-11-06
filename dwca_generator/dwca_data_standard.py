#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import zipfile

import dwca_generator

class DwcaDataSharkStandard():
    """ Contains a list of all data rows stored as dictionaries.
        Each row doctionary contains fields both for the internal format and DwC. 
    """
    def __init__(self, resources):
        """ """
        # Reference to DwcaResources object. 
        self.resources = resources
        # List ofdictionaries containing all data rows.
        self.row_list = []
        # Lookup dictionary for keys to avoid duplicates.
        self.dwc_short_names_exists_dict = {}
        # Field mappning between internal and DwC fields.
        self.dwc_default_mapping = {}
    
    def get_data_rows(self):
        """ """
        return self.row_list
    
    def add_dataset(self, dataset_filepath):
        """ Add data from SHARK zipped files."""
        header = []
        # From file in zip to list of rows.
        with zipfile.ZipFile(dataset_filepath) as z:
            with z.open('shark_data.txt', 'r') as f:
                for index, row in enumerate(f):
                    row = row.decode("cp1252")
                    row_items = [str(x.strip()) for x in row.split('\t')]
                    if index == 0:
                        header = row_items
                    else:
                        row_dict = dict(zip(header, row_items))
                        # Add to list.
                        self.row_list.append(row_dict)
    
    def cleanup_data(self):
        """ """
        for row_dict in self.row_list:
            try:
                sample_date_str = str(row_dict['sample_date'])
    #             row_dict['year'] = sample_date_str[0:4]
                row_dict['month'] = sample_date_str[5:7]
                row_dict['day'] = sample_date_str[8:10]
            except:
                pass
             
            # Time zone info. (+01:00 or +02:00 (DST=Daylight Savings Time) for Sweden. 
            event_date = row_dict.get('eventDate', '')
            event_time = row_dict.get('eventTime', '')
            if (event_time != '') and (event_time != ''):
                if dwca_generator.is_daylight_savings_time(event_date):
                    row_dict['eventTime'] = event_time + '+02:00'
                else:
                    row_dict['eventTime'] = event_time + '+01:00'
    
    def add_extra_fields(self):
        """ """
        for row_dict in self.row_list:
            for key, value in self.resources.get_extra_fields().items():
                row_dict[key] = value
    
    def create_dwca_keys(self):
        """ """
        for row_dict in self.row_list:
            
            # Extra keys for the "event.txt" table.
            for _dwc_node_name, dwc_node_dict in self.resources.get_event_nodes().items():
                
                dwc_key_name = dwc_node_dict.get('dwc_key_name', '')
                dwc_key_prefix = dwc_node_dict.get('dwc_key_prefix', '')
                key_list = dwc_node_dict.get('key_fields', [])
                dwc_id = dwca_generator.create_extra_key(row_dict, key_list)
                
                # Used to generate short names.
                if dwc_key_name not in self.dwc_short_names_exists_dict:
                    self.dwc_short_names_exists_dict[dwc_key_name] = {}
                    self.dwc_short_names_exists_dict[dwc_key_name]['seq_no'] = 0
                    self.dwc_short_names_exists_dict[dwc_key_name]['short_ids'] = {}
                
                if dwc_id not in self.dwc_short_names_exists_dict[dwc_key_name]['short_ids'].keys():
                    seq_no = self.dwc_short_names_exists_dict[dwc_key_name]['seq_no']
                    seq_no += 1
                    self.dwc_short_names_exists_dict[dwc_key_name]['seq_no'] = seq_no
                    self.dwc_short_names_exists_dict[dwc_key_name]['short_ids'][dwc_id] = seq_no
                #
                seq_no = self.dwc_short_names_exists_dict[dwc_key_name]['short_ids'][dwc_id]
                dwc_id_short = dwc_key_prefix + str(seq_no)
                row_dict[dwc_key_name] = dwc_id_short
            
            # Extra keys for the "occurrence.txt" table.
            for _dwc_node_name, dwc_node_dict in self.resources.get_occurrence_nodes().items():
                
                dwc_key_name = dwc_node_dict.get('dwc_key_name', '')
                dwc_key_prefix = dwc_node_dict.get('dwc_key_prefix', '')
                key_list = dwc_node_dict.get('key_fields', [])
                dwc_id = dwca_generator.create_extra_key(row_dict, key_list)
                
                # Used to generate short names.
                if dwc_key_name not in self.dwc_short_names_exists_dict:
                    self.dwc_short_names_exists_dict[dwc_key_name] = {}
                    self.dwc_short_names_exists_dict[dwc_key_name]['seq_no'] = 0
                    self.dwc_short_names_exists_dict[dwc_key_name]['short_ids'] = {}
                
                if dwc_id not in self.dwc_short_names_exists_dict[dwc_key_name]['short_ids'].keys():
                    seq_no = self.dwc_short_names_exists_dict[dwc_key_name]['seq_no']
                    seq_no += 1
                    self.dwc_short_names_exists_dict[dwc_key_name]['seq_no'] = seq_no
                    self.dwc_short_names_exists_dict[dwc_key_name]['short_ids'][dwc_id] = seq_no
                #
                seq_no = self.dwc_short_names_exists_dict[dwc_key_name]['short_ids'][dwc_id]
                dwc_id_short = dwc_key_prefix + str(seq_no)
                row_dict[dwc_key_name] = dwc_id_short
            
            # Extra keys for the "extendedmeasurementorfact.txt" table.
            parameter = row_dict.get('parameter', '')
            unit = row_dict.get('unit', '')
            dwc_id_emof = dwc_id + ',param:' + parameter + ',unit:' + unit
            row_dict['emof_param_unit_id'] = dwc_id_emof
    
#         for row_dict in self.row_list:
#             
#             # Extra keys for the "event.txt" table.
#             for _dwc_node_name, dwc_node_dict in self.resources.get_event_nodes().items():
#                 
#                 dwc_key_name = dwc_node_dict.get('dwc_key_name', '')
#                 dwc_key_prefix = dwc_node_dict.get('dwc_key_prefix', '')
#                 key_list = dwc_node_dict.get('key_fields', [])
#                 dwc_id = dwca_generator.create_extra_key(row_dict, key_list)
#                 
#                 # Used to generate short names.
#                 if dwc_key_name not in self.dwc_short_names_exists_dict:
#                     self.dwc_short_names_exists_dict[dwc_key_name] = {}
#                     self.dwc_short_names_exists_dict[dwc_key_name]['seq_no'] = 0
#                     self.dwc_short_names_exists_dict[dwc_key_name]['short_ids'] = set()
#                 
#                 if dwc_id not in self.dwc_short_names_exists_dict[dwc_key_name]['short_ids']:
#                     seq_no = self.dwc_short_names_exists_dict[dwc_key_name]['seq_no']
#                     seq_no += 1
#                     self.dwc_short_names_exists_dict[dwc_key_name]['seq_no'] = seq_no
#                     self.dwc_short_names_exists_dict[dwc_key_name]['short_ids'].add(dwc_id)
#                 #
#                 seq_no = self.dwc_short_names_exists_dict[dwc_key_name]['seq_no']
#                 dwc_id_short = dwc_key_prefix + str(seq_no)
#                 row_dict[dwc_key_name] = dwc_id_short
#             
#             # Extra keys for the "occurrence.txt" table.
#             for _dwc_node_name, dwc_node_dict in self.resources.get_occurrence_nodes().items():
#                 
#                 dwc_key_name = dwc_node_dict.get('dwc_key_name', '')
#                 dwc_key_prefix = dwc_node_dict.get('dwc_key_prefix', '')
#                 key_list = dwc_node_dict.get('key_fields', [])
#                 dwc_id = dwca_generator.create_extra_key(row_dict, key_list)
#                 
#                 # Used to generate short names.
#                 if dwc_key_name not in self.dwc_short_names_exists_dict:
#                     self.dwc_short_names_exists_dict[dwc_key_name] = {}
#                     self.dwc_short_names_exists_dict[dwc_key_name]['seq_no'] = 0
#                     self.dwc_short_names_exists_dict[dwc_key_name]['short_ids'] = set()
#                 
#                 if dwc_id not in self.dwc_short_names_exists_dict[dwc_key_name]['short_ids']:
#                     seq_no = self.dwc_short_names_exists_dict[dwc_key_name]['seq_no']
#                     seq_no += 1
#                     self.dwc_short_names_exists_dict[dwc_key_name]['seq_no'] = seq_no
#                     self.dwc_short_names_exists_dict[dwc_key_name]['short_ids'].add(dwc_id)
#                 #
#                 seq_no = self.dwc_short_names_exists_dict[dwc_key_name]['seq_no']
#                 dwc_id_short = dwc_key_prefix + str(seq_no)
#                 row_dict[dwc_key_name] = dwc_id_short
#             
#             # Extra keys for the "extendedmeasurementorfact.txt" table.
#             parameter = row_dict.get('parameter', '')
#             unit = row_dict.get('unit', '')
#             dwc_id_emof = dwc_id + ',param:' + parameter + ',unit:' + unit
#             row_dict['emof_param_unit_id'] = dwc_id_emof
    
    def map_fields_to_dwc(self):
        """ """
        default_mapping = self.get_default_mapping()
        # Apply on all data rows.
        for row_dict in self.row_list:
            try:
                for dwc_key, shark_key in default_mapping.items():
                    value = str(row_dict.get(shark_key, ''))
                    if value:
                        row_dict[dwc_key] = value
            except Exception as e:
                print('DEBUG Exception:', e)
                raise
    
    def get_default_mapping(self):
        """ """
        if not self.dwc_default_mapping:
            self.dwc_default_mapping = {}
                
            for key, mapping_dict in self.resources.get_field_mapping().items():
                self.dwc_default_mapping[key] = mapping_dict.get('source_field', '')
        #
        return self.dwc_default_mapping
    