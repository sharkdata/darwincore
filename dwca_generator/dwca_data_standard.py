#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import zipfile

import dwca_generator

class DwcaDataSharkStandard():
    """ Contains a list of all data rows stored as dictionaries.
        Each row doctionary contains fields both for the internal format and DwC. 
    """
    def __init__(self, resources, target_dwca_path='DwC-A_TEST.zip'):
        """ """
        self.target_dwca_path = pathlib.Path(target_dwca_path)
        # Reference to DwcaResources object. 
        self.resources = resources
        # List ofdictionaries containing all data rows.
        self.row_list = []
        # Lookup dictionary for keys to avoid duplicates.
        self.dwc_short_names_exists_dict = {}
        # Field mappning between internal and DwC fields.
        self.dwc_default_mapping = {}
        # List of keys for dynamic fields.
        self.used_dynamic_field_key_list = []
    
    def get_data_rows(self):
        """ """
        return self.row_list
    
    def add_shark_dataset(self, dataset_filepath):
        """ Add data from SHARK zipped files. """
        try:
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
                            
                            # Check filter. Don't add filtered rows.
                            add_row = True
                            for filter_column_name, filter_dict in self.resources.get_filters().items():
                                value = row_dict.get(filter_column_name, '')
                                if value:
                                    included_values = filter_dict.get('included_values', None)
                                    excluded_values = filter_dict.get('excluded_values', None)
                                    if included_values and (value not in included_values):
                                        add_row = False
                                    if excluded_values and (value in excluded_values):
                                        add_row = False
                            
                            # Add to list.
                            if add_row:
                                # Translate values.
                                for key in self.resources.get_translate_from_source_keys():
                                    value = row_dict.get(key, '')
                                    if value:
                                        new_value = self.resources.get_translate_from_source(key, value)
                                        if value != new_value:
                                            row_dict[key] = new_value
                                # Append.
                                self.row_list.append(row_dict)
        except Exception as e:
            print('Exception: ', str(dataset_filepath), e)
    
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
            sample_date = row_dict.get('sample_date', '')
            sample_time = row_dict.get('sample_time', '')
            if (sample_date != '') and (sample_time != ''):
                if dwca_generator.is_daylight_savings_time(sample_date):
                    row_dict['sample_time'] = sample_time + '+02:00'
                else:
                    row_dict['sample_time'] = sample_time + '+01:00'
    
    def create_dwca_keys(self):
        """ """
        for row_dict in self.row_list:
            
            # Extra keys for the "event.txt" table.
            for _dwc_event_node_name, dwc_event_node_dict in self.resources.get_event_nodes_keys().items():
                
                dwc_key_name = dwc_event_node_dict.get('dwc_key_name', '')
                dwc_key_prefix = dwc_event_node_dict.get('dwc_key_prefix', '')
                key_list = dwc_event_node_dict.get('key_fields', [])
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
            for _dwc_event_node_name, dwc_event_node_dict in self.resources.get_occurrence_nodes_keys().items():
                
                scientific_name = row_dict.get('scientific_name', '')
                if not scientific_name:
                    continue
                #
                dwc_key_name = dwc_event_node_dict.get('dwc_key_name', '')
                dwc_key_prefix = dwc_event_node_dict.get('dwc_key_prefix', '')
                key_list = dwc_event_node_dict.get('key_fields', [])
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
    
    def create_dynamic_fields(self):
        """ """
        # Create dict with list for each dwc_event_node/dwc_dynamic_filed pair.
        node_dynfield_dict = {}
        for row_dict in self.resources.dwc_dynamic_fields[:]:
            dwc_category = row_dict.get('dwc_category', '')
            dwc_event_node = row_dict.get('dwc_event_node', '')
            dwc_dynamic_field = row_dict.get('dwc_dynamic_field', '')
            if dwc_event_node and dwc_dynamic_field:
                node_dynfield_key = dwc_category + '<+>' + dwc_event_node + '<+>' + dwc_dynamic_field
                if node_dynfield_key not in node_dynfield_dict.keys():
                    node_dynfield_dict[node_dynfield_key] = {}
                    node_dynfield_dict[node_dynfield_key]['key_value_list'] = [] # Used for fix text fields.
                    node_dynfield_dict[node_dynfield_key]['source_fields_dynamic_fields'] = []
        # Loop over list of dynamic fields. Store fix text as key/value and column name for later use.
        for row_dict in self.resources.dwc_dynamic_fields:
            dwc_category = row_dict.get('dwc_category', '')
            dwc_event_node = row_dict.get('dwc_event_node', '')
            dwc_dynamic_field = row_dict.get('dwc_dynamic_field', '')
            node_dynfield_key = dwc_category + '<+>' + dwc_event_node + '<+>' + dwc_dynamic_field
            dwc_dynamic_key = row_dict.get('dwc_dynamic_key', '')
            source_field = row_dict.get('source_field', '')
            text = row_dict.get('text', '')
            #
            node_dynfield_dict[node_dynfield_key]['dwc_dynamic_field'] = dwc_dynamic_field
            node_dynfield_dict[node_dynfield_key]['node_dynfield_key'] = node_dynfield_key
            node_dynfield_dict[node_dynfield_key]['dwc_dynamic_key'] = dwc_dynamic_key
            #
            if text:
                node_dynfield_dict[node_dynfield_key]['key_value_list'].append(dwc_dynamic_key + ': ' + text)
            elif source_field:
                node_dynfield_dict[node_dynfield_key]['source_fields_dynamic_fields'].append((source_field, dwc_dynamic_key))
            
        # Loop over rows.
        for row_dict in self.row_list:
            for node_dynfield in node_dynfield_dict.values():
                source_field = ''
                node_dynfield_key = node_dynfield['node_dynfield_key']
                key_value_list = node_dynfield['key_value_list'][:]
                
                for (source_field, dwc_dynamic_key) in node_dynfield['source_fields_dynamic_fields']:
                    if source_field:
                        value = row_dict.get(source_field, '')
                        if value:
                            key_value_list.append(dwc_dynamic_key + ': ' + value)
                #
                dynamic_string = ', '.join(key_value_list)
                if dynamic_string:
                    row_dict[node_dynfield_key] = dynamic_string
                    
                    if node_dynfield_key not in self.used_dynamic_field_key_list:
                        self.used_dynamic_field_key_list.append(node_dynfield_key)
                        
    def get_used_dynamic_field_keys(self):
        """ """
        return self.used_dynamic_field_key_list

