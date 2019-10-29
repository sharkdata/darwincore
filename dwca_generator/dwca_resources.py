#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import openpyxl

class DwcaResources():
    """ """
    def __init__(self):
        """ """
        # Raw lists from Excel file.
        self.dwca_columns = [] 
        self.event_keys = [] 
        self.occurrence_keys = [] 
        self.mof_keys = [] 
        self.field_mapping = [] 
        self.extra_fields = [] 
        self.dynamic_fields = [] 
        self.dataset_filter = [] 
        self.metadata = [] 
        self.metadata_sources = [] 
        self.data_sources = [] 
        self.readme = [] 
        # Processed content.
        self.dwca_columns_dict = None 
        self.field_mapping_dict = None
        self.extra_fields_dict = None
        self.dwc_event_nodes = None
        self.dwc_occurrence_nodes = None
        self.fields_for_each_node = None
    
    def get_dwca_columns(self):
        """ """
        if not self.dwca_columns_dict:
            self.dwca_columns_dict = {}
            for row in self.dwca_columns:
                for key, value in row.items():
                    if value:
                        if not value[0] == '#':
                            if key not in self.dwca_columns_dict:
                                self.dwca_columns_dict[key] = []
                            #
                            self.dwca_columns_dict[key].append(value)
            
        return self.dwca_columns_dict
    
    def get_event_node_names(self):
        """ """
        self.get_event_nodes()
        
        return self.dwc_event_nodes.keys()
    
    def get_event_nodes(self):
        """ """
        if not self.dwc_event_nodes:
            self.dwc_event_nodes = {}
            for row_dict in self.event_keys:
                
                dwc_event_node = row_dict.get('dwc_event_node', '')
                dwc_parent_event_node = row_dict.get('dwc_parent_event_node', '')
                dwc_key = row_dict.get('dwc_key', '')
                dwc_key_prefix = row_dict.get('dwc_key_prefix', '')
                
                if dwc_event_node:
                    if dwc_event_node not in self.dwc_event_nodes:
                        self.dwc_event_nodes[dwc_event_node] = {}
                        node_dict = self.dwc_event_nodes[dwc_event_node]
                        node_dict['dwc_event_node'] = dwc_event_node
                        node_dict['dwc_parent_event_node'] = dwc_parent_event_node
                        node_dict['dwc_key'] = dwc_key
                        node_dict['dwc_key_prefix'] = dwc_key_prefix
                        node_dict['key_fields'] = []
                        for key in ['key_1', 'key_2', 'key_3', 'key_4', 'key_5', 
                                    'key_6', 'key_7', 'key_8', 'key_9', 'key_10', ]:
                            value = row_dict.get(key, '')
                            if value:
                                node_dict['key_fields'].append(value)
                        #    
                        print(node_dict)
            
        return self.dwc_event_nodes
    
    def get_occurrence_nodes(self):
        """ """
        if not self.dwc_occurrence_nodes:
            self.dwc_occurrence_nodes = {}
            for row_dict in self.occurrence_keys:
                
                dwc_event_node = row_dict.get('dwc_event_node', '')
                dwc_key = row_dict.get('dwc_key', '')
                dwc_event_key = row_dict.get('dwc_event_key', '')
                dwc_key_prefix = row_dict.get('dwc_key_prefix', '')
                
                if dwc_event_node:
                    if dwc_event_node not in self.dwc_occurrence_nodes:
                        self.dwc_occurrence_nodes[dwc_event_node] = {}
                        node_dict = self.dwc_occurrence_nodes[dwc_event_node]
                        node_dict['dwc_event_node'] = dwc_event_node
                        node_dict['dwc_key'] = dwc_key
                        node_dict['dwc_event_key'] = dwc_event_key
                        node_dict['dwc_key_prefix'] = dwc_key_prefix
                        node_dict['key_fields'] = []
                        for key in ['key_1', 'key_2', 'key_3', 'key_4', 'key_5', 
                                    'key_6', 'key_7', 'key_8', 'key_9', 'key_10', ]:
                            value = row_dict.get(key, '')
                            if value:
                                node_dict['key_fields'].append(value)
                        #
                        print(node_dict)
        
        return self.dwc_occurrence_nodes
    
    def get_fields_for_each_node(self, node_name):
        """ """
        if not self.fields_for_each_node:
            self.fields_for_each_node = {}
            for row_dict in self.field_mapping:
                dwc_node = row_dict.get('dwc_node', '')
                dwc_field = row_dict.get('dwc_field', )
                if dwc_field:
                    if dwc_node not in self.fields_for_each_node:
                        self.fields_for_each_node[dwc_node] = []
                    self.fields_for_each_node[dwc_node].append(dwc_field)
        # 
        return self.fields_for_each_node[node_name]
    
    def get_field_mapping(self):
        """ """
        if not self.field_mapping_dict:
            self.field_mapping_dict = {}
            for row_dict in self.field_mapping:
                if 'dwc_field' in row_dict:
                    self.field_mapping_dict[row_dict['dwc_field']] = row_dict.get('shark_field', '')
        # 
        return self.field_mapping_dict
    
    def get_extra_fields(self):
        """ """
        if not self.extra_fields_dict:
            self.extra_fields_dict = {}
            for row_dict in self.extra_fields:
                if 'dwc_field' in row_dict:
                    self.extra_fields_dict[row_dict['dwc_field']] = row_dict.get('text', '')
        # 
        return self.extra_fields_dict
    
    def load_from_excel(self, excel_file_path):
        """ """
        excel_file_path = pathlib.Path(excel_file_path)
        workbook = None
        try:
            workbook = openpyxl.load_workbook(filename=excel_file_path)
            
            for sheet_name in workbook.sheetnames:
                print('Excel sheet: ', sheet_name)
                
                worksheet = workbook[sheet_name]
                
                if sheet_name == 'dwca_columns':
                    self._local_read_excel_sheet(worksheet, self.dwca_columns)
                if sheet_name == 'event_keys':
                    self._local_read_excel_sheet(worksheet, self.event_keys)
                if sheet_name == 'occurrence_keys':
                    self._local_read_excel_sheet(worksheet, self.occurrence_keys)
                if sheet_name == 'mof_keys':
                    self._local_read_excel_sheet(worksheet, self.mof_keys)
                if sheet_name == 'field_mapping':
                    self._local_read_excel_sheet(worksheet, self.field_mapping)
                if sheet_name == 'extra_fields':
                    self._local_read_excel_sheet(worksheet, self.extra_fields)
                if sheet_name == 'dynamic_fields':
                    self._local_read_excel_sheet(worksheet, self.dynamic_fields)
                if sheet_name == 'dataset_filter':
                    self._local_read_excel_sheet(worksheet, self.dataset_filter)
                if sheet_name == 'metadata':
                    self._local_read_excel_sheet(worksheet, self.metadata)
                if sheet_name == 'metadata_sources':
                    self._local_read_excel_sheet(worksheet, self.metadata_sources)
                if sheet_name == 'data_sources':
                    self._local_read_excel_sheet(worksheet, self.data_sources)
                if sheet_name == 'README':
                    self._local_read_excel_sheet(worksheet, self.readme)
        finally:
            if workbook:
                workbook.close()
    
    def _local_read_excel_sheet(self, excel_sheet, target_list):
        """ Local function """
        header = []
        for rowindex, row in enumerate(excel_sheet.iter_rows()):
            if rowindex == 0:
                # Header.
                for cell in row:
                    value = cell.value
                    if value == None:
                        header.append('')
                    else:
                        header.append(str(value).strip())
                        
                if len(''.join(header)) == 0:
                    return # Header row is mandatory.
            else:
                # Row.
                newrow = []
                for cell in row:
                    value = cell.value
                    if value == None:
                        newrow.append('')
                    else:
                        newrow.append(str(value).strip())
                
                if len(''.join(newrow)) == 0:
                    continue # Don't add empty rows.
                
                row_dict = dict(zip(header, newrow))
                target_list.append(row_dict)
    
    
##### TEST #####
# if __name__ == "__main__":
#     """ """
#     config = DwcaResources()
#     config.load_config_from_excel('dwca_matrix_default.xlsx')
#     print(config.get_dwca_columns())
#     print(config.get_event_node_names())
#     print(config.get_event_nodes())
#     print(config.get_occurrence_nodes())
#     print(config.get_extra_fields())
#     print('Test done.')
    