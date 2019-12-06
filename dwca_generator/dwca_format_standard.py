#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import copy
import datetime

import dwca_generator

class DwcaFormatStandard(object):
    """ """
    def __init__(self, data=None, resources=None, species_info=None ):
        """ Darwin Core Archive Format base class. """
        
        self.data_object = data
        self.resources_object = resources
        self.species_info_object = species_info
        
        self.worms_info_object = None
        #
        self.dwca_event_columns = []
        self.dwca_occurrence_columns = []
        self.dwca_measurementorfact_columns = []
        self.mof_extra_params = None
        #
        self._taxa_lookup_dict = {}
        #
        self.clear()
     
    def clear(self):
        """ """
        self.target_rows = []
        self.dwca_event = [] 
        self.dwca_occurrence = [] 
        self.dwca_measurementorfact = [] 
        #
        self.meta_file_name = None
        self.eml_file_name = None
     
    def create_dwca_parts(self):
        """ """
        self.target_rows = self.data_object.get_data_rows()
        
        self.create_dwca_event()
        
        self.create_dwca_occurrence()
         
        self.create_dwca_measurementorfact()
    
    def create_dwca_event(self):
        """ """
        # Get node name hierarchy.
        event_node_names = self.resources_object.get_event_node_names()
        # Get all node info.
        event_nodes = self.resources_object.get_event_nodes()
        # Used for dynamicProperties.
        used_dynamic_field_key_list = self.data_object.get_used_dynamic_field_keys()
        
        # Create control dictionary.
        event_control_dict = {}
        for event_node_name in event_node_names:
            if event_node_name not in event_control_dict:
                event_control_dict[event_node_name] = {}
                event_control_dict[event_node_name]['used_key_list'] = set()
                event_control_dict[event_node_name]['dwc_key_name'] = event_nodes[event_node_name]['dwc_key_name']
                event_control_dict[event_node_name]['fields'] = self.resources_object.get_event_node_fields(event_node_name)
        # Process all data rows.
        for target_row in self.target_rows:
            #
            if target_row.get('remove_row', '') == '<REMOVE>':
                continue
            # Iterate over nodes.
            parent_node_key = ''
            for event_node_name in event_node_names:
                # Current row in control dictionary.
                control_dict = event_control_dict[event_node_name]
                # Get keys.
                node_key = target_row.get(control_dict['dwc_key_name'], '')
                # Create event row.
                if node_key and (node_key not in control_dict['used_key_list']):
                    control_dict['used_key_list'].add(node_key)
                    #
                    event_dict = {}
                    for column_name in control_dict['fields']:
                        event_dict[column_name] = target_row.get(column_name, '')
                    #
                    event_dict['type'] = event_node_name
                    event_dict['id'] = node_key
                    event_dict['eventID'] = node_key
                    event_dict['parentEventID'] = parent_node_key
                    
                    # Add key to dynamicProperties.
                    for dynamic_field_key in used_dynamic_field_key_list:
                        if event_node_name + '<->' in dynamic_field_key:
                            # Remove dwc_event_node part from key.
                            new_key = dynamic_field_key.replace(event_node_name + '<->', '')
                            event_dict[new_key] = target_row.get(dynamic_field_key, '')
                    #
                    self.dwca_event.append(event_dict) 
                
                parent_node_key = node_key
     
    def create_dwca_occurrence(self):
        """ """
        # Get all node info.
        occurrence_nodes = self.resources_object.get_occurrence_nodes()
        
        
        
        
#         occurrence_node = occurrence_nodes['occurrence']
        occurrence_node = occurrence_nodes['sample']
        
        
        
        
        # Used for dynamicProperties.
        used_dynamic_field_key_list = self.data_object.get_used_dynamic_field_keys()
        # Create control dictionary.
        used_key_list = set()
        dwc_event_key_name = occurrence_node['dwc_event_key']
        dwc_key_name = occurrence_node['dwc_key_name']
#         occurrence_fields = self.resources_object.get_event_node_fields('occurrence')
        occurrence_fields = self.resources_object.get_dwc_columns().get('dwc_occurrence_columns', [])
        
        # Process all data rows.
        for target_row in self.target_rows:
            #
            if target_row.get('remove_row', '') == '<REMOVE>':
                continue
            #
            scientific_name = target_row.get('scientific_name', '')
            if scientific_name == '':
                continue
            #
            # Get keys.
            dwc_event_key = target_row.get(dwc_event_key_name, '')
            occurrence_key = target_row.get(dwc_key_name, '')
            # Create event row.
            if occurrence_key and (occurrence_key not in used_key_list):
                used_key_list.add(occurrence_key)
                #
                occurrence_dict = {}
                    
                for occurrence_field in occurrence_fields:
                    value = target_row.get(occurrence_field, '')
                    if value:
                        occurrence_dict[occurrence_field] = target_row.get(occurrence_field, '')
                #
#                     occurrence_dict['type'] = event_node_name
#                     occurrence_dict['id'] = node_key
#                     occurrence_dict['eventID'] = target_row['eventID']
#                     occurrence_dict['parentEventID'] = parent_node_key
                #
                
                occurrence_dict['id'] = dwc_event_key
                occurrence_dict['eventID'] = dwc_event_key
                occurrence_dict['occurrenceID'] = occurrence_key
                
                
                # Add key to dynamicProperties.
                for dynamic_field_key in used_dynamic_field_key_list:
                    if 'occurrence<->' in dynamic_field_key:
                        # Remove dwc_event_node part from key.
                        new_key = dynamic_field_key.replace('occurrence<->', '')
                        occurrence_dict[new_key] = target_row.get(dynamic_field_key, '')
                 
                #
                taxa_info_dict = self.species_info_object.get_info_as_dwc_dict(source_dict=occurrence_dict)
                occurrence_dict.update(taxa_info_dict)
                
                self.dwca_occurrence.append(occurrence_dict) 
            
            
            
#             #
#             dwca_occurrence_id = target_row.get('occurrence_key', '')
#             dwca_sample_id_short = target_row.get('sample_key', '')
#             #
#             if dwca_occurrence_id and (dwca_occurrence_id not in used_occurrence_key_list):
#                 used_occurrence_key_list.add(dwca_occurrence_id)
#                 #
#                 if scientific_name in self._taxa_lookup_dict:
#                     occurrence_dict = copy.deepcopy(self._taxa_lookup_dict[scientific_name])
#                 else:
#                     taxa_dict = dwca_generator.TranslateTaxa().get_translated_aphiaid_and_name(scientific_name)
#                     # Taxa info.
#                     occurrence_dict = {}
#                     #
#                     dyntaxa_id = taxa_dict.get('dyntaxa_id', '')
#                     if dyntaxa_id:
#                         occurrence_dict['taxonID'] = 'urn:lsid:dyntaxa.se:Taxon:' + dyntaxa_id
#                     else:
#                         occurrence_dict['taxonID'] = ''
#                     #
#                     occurrence_dict['scientificNameID'] = taxa_dict.get('worms_lsid', '')
# #                     occurrence_dict['worms_scientific_name'] = taxa_dict.get('worms_scientific_name', '')            
#                     occurrence_dict['taxonRank'] = taxa_dict.get('worms_rank', '')
#                     occurrence_dict['kingdom'] = taxa_dict.get('worms_kingdom', '')
#                     occurrence_dict['phylum'] = taxa_dict.get('worms_phylum', '')
#                     occurrence_dict['class'] = taxa_dict.get('worms_class', '')
#                     occurrence_dict['order'] = taxa_dict.get('worms_order', '')
#                     occurrence_dict['family'] = taxa_dict.get('worms_family', '')
#                     occurrence_dict['genus'] = taxa_dict.get('worms_genus', '')
#                     #
#                     self._taxa_lookup_dict[scientific_name] = copy.deepcopy(occurrence_dict)
#                                  
#                 # Direct field mapping.
#                 for column_name in self.get_occurrence_columns():
#                     value = str(target_row.get(column_name, ''))
#                     if value:
#                         occurrence_dict[column_name] = value
#                 #
#                 occurrence_dict['id'] = dwca_sample_id_short
#                 occurrence_dict['eventID'] = dwca_sample_id_short
#                 occurrence_dict['occurrenceID'] = dwca_occurrence_id
# #                 # Add key to dynamicProperties.
# #                 occurrence_dict['dynamicProperties'] = dwca_occurrence_id
#                 #
#                 self.dwca_occurrence.append(occurrence_dict) 
     
    def create_dwca_measurementorfact(self):
        """ """
        used_mof_occurrence_key_list = set()
        generated_parameters_key_list = set()
        debug_row_number = 0
        
        # Used for dynamicProperties.
        used_dynamic_field_key_list = self.data_object.get_used_dynamic_field_keys()
        # Get node name hierarchy.
        event_node_names = self.resources_object.get_event_node_names()
        # Get all node info.
        event_nodes = self.resources_object.get_event_nodes()
        # Create control dictionary.
        event_control_dict = {}
        for event_node_name in event_node_names:
            if event_node_name not in event_control_dict:
                event_control_dict[event_node_name] = {}
                event_control_dict[event_node_name]['dwc_key_name'] = event_nodes[event_node_name]['dwc_key_name']
                event_control_dict[event_node_name]['dwc_event_key'] = event_nodes[event_node_name].get('dwc_event_key', '')
                event_control_dict[event_node_name]['used_key_list'] = set()
                event_control_dict[event_node_name]['used_extra_params_list'] = set()
                event_control_dict[event_node_name]['emof_extra_params'] = {}
         
        for dwc_keys_row in self.resources_object.dwc_keys:

            
            
#             if dwc_keys_row.get('dwc_event_node', '') == 'occurrence':
            if dwc_keys_row.get('dwc_event_node', '') == 'sample':

                
                
                
                occurrence_dwc_category = dwc_keys_row.get('dwc_category', '')
                occurrence_dwc_event_node = dwc_keys_row.get('dwc_event_node', '')
                occurrence_dwc_parent_event = dwc_keys_row.get('dwc_parent_event', '')
                occurrence_dwc_key_name = dwc_keys_row.get('dwc_key_name', '')
                occurrence_dwc_event_key = dwc_keys_row.get('dwc_event_key', '')
                occurrence_dwc_key_prefix = dwc_keys_row.get('dwc_key_prefix', '')
         
        for target_row in self.target_rows:
            #
            if target_row.get('remove_row', '') == '<REMOVE>':
                continue
            
            # Iterate over nodes.
            parent_node_key = ''
            for event_node_name in event_node_names:
                # Current row in control dictionary.
                control_dict = event_control_dict[event_node_name]
                # Get keys.
                event_node_key = target_row.get(control_dict['dwc_key_name'], '')
                # Create event row.
                if event_node_key and (event_node_key not in control_dict['used_key_list']):
                    control_dict['used_key_list'].add(event_node_key)
                    #
                    # Extra parameters connected to events, not occurences.
                    if event_node_key and (event_node_key not in control_dict['used_extra_params_list']):
                        control_dict['used_extra_params_list'].add(event_node_key)
                        
                        for field_mapping_row in self.resources_object.field_mapping:
                            if field_mapping_row.get('dwc_event_node', '') is not event_node_name:
                                continue
                            source_field = field_mapping_row.get('source_field', '')
                            dwc_measurement_type = field_mapping_row.get('dwc_measurement_type', '')
                            dwc_measurement_unit = field_mapping_row.get('dwc_measurement_unit', '')
                            if source_field and dwc_measurement_type:
                                event_control_dict[event_node_name]['emof_extra_params'][source_field] = ( dwc_measurement_type , dwc_measurement_unit )
                         
                        for key, (param, unit) in event_control_dict[event_node_name]['emof_extra_params'].items(): 
                            value = str(target_row.get(key, ''))
                            if value: 
                                measurementorfact_dict = {} 
                                measurementorfact_dict['id'] = event_node_key
                                measurementorfact_dict['eventID'] = event_node_key
                                measurementorfact_dict['measurementType'] = param 
                                measurementorfact_dict['measurementValue'] = value 
                                measurementorfact_dict['measurementUnit'] = unit 
                                measurementorfact_dict['measurementDeterminedDate'] = target_row.get('sample_date', '') 
                                    
                                    
                                    
                        # Add key to dynamicProperties.
                        for dynamic_field_key in used_dynamic_field_key_list:
                            if 'emof<->' in dynamic_field_key:
                                # Remove dwc_event_node part from key.
                                new_key = dynamic_field_key.replace('emof<->', '')
                                measurementorfact_dict[new_key] = target_row.get(dynamic_field_key, '')
                            
                            
                            
                        #
                        self.dwca_measurementorfact.append(measurementorfact_dict) 
                
                
                # Used if row contains species.
                if event_node_name == occurrence_dwc_parent_event:
                    dwc_key = target_row.get(occurrence_dwc_key_name, '')
                    dwc_event_key = target_row.get(occurrence_dwc_event_key, '')
                    emof_param_unit_id = target_row.get('emof_param_unit_id', '')
                    
                    occurrence_key = dwc_key
                    if dwc_key == dwc_event_key:
                        occurrence_key = ''
         
                    if emof_param_unit_id and (emof_param_unit_id not in used_mof_occurrence_key_list):
                        used_mof_occurrence_key_list.add(emof_param_unit_id)
                     
                        parameter = target_row.get('parameter', '')
                        value = target_row.get('value', '')
                        unit = target_row.get('unit', '')
                        if parameter:
                            measurementorfact_dict = {}
                            measurementorfact_dict['id'] = dwc_event_key
                            measurementorfact_dict['eventID'] = dwc_event_key
                            measurementorfact_dict['occurrenceID'] = occurrence_key
                            measurementorfact_dict['measurementType'] = parameter
                            measurementorfact_dict['measurementValue'] = value
                            measurementorfact_dict['measurementUnit'] = unit
                            measurementorfact_dict['measurementAccuracy'] = ''
                            measurementorfact_dict['measurementDeterminedDate'] = target_row.get('measurementDeterminedDate', '')
                            measurementorfact_dict['measurementDeterminedBy'] = target_row.get('measurementDeterminedBy', '')
                            measurementorfact_dict['measurementMethod'] = target_row.get('measurementMethod', '') # TODO: method_reference_code
                            measurementorfact_dict['measurementRemarks'] = target_row.get('measurementRemarks', '')
                            #
                            
                            
                                            
                            # Add key to dynamicProperties.
                            for dynamic_field_key in used_dynamic_field_key_list:
                                if 'emof<->' in dynamic_field_key:
                                    # Remove dwc_event_node part from key.
                                    new_key = dynamic_field_key.replace('emof<->', '')
                                    measurementorfact_dict[new_key] = target_row.get(dynamic_field_key, '')
                                    
                                    
                                    
                            #
                            self.dwca_measurementorfact.append(measurementorfact_dict)
                             
                             
                             
                            # Add parameter for size_class.
                            size_class = target_row.get('size_class', '')
                            if size_class:
                                if dwc_key not in generated_parameters_key_list:
                                    generated_parameters_key_list.add(dwc_key)
                                    #
                                    measurementorfact_dict_2 = copy.deepcopy(measurementorfact_dict)
        #                             measurementorfact_dict_2['id'] = self.measurementorfact_seq_no
        #                             self.measurementorfact_seq_no += 1
                                    #
                                    measurementorfact_dict_2['measurementType'] = 'SizeClass(HELCOM-PEG)'
                                    measurementorfact_dict_2['measurementValue'] = size_class
                                    measurementorfact_dict_2['measurementUnit'] = ''
                                    #
                                    self.dwca_measurementorfact.append(measurementorfact_dict_2)
                             
                             
                    else:
                        if debug_row_number < 100:
                            try:
                                print('DEBUG Duplicates: emof_param_unit_id: ' + str(emof_param_unit_id))
                            except Exception as e:
                                print('DEBUG Exception: ' + str(e))
                            debug_row_number += 1
                        elif debug_row_number == 100:
                            print('DEBUG: MAX LIMIT OF 100 LOG ROWS.')
                            debug_row_number += 1
    
    def extract_metadata(self):
        """ """
        latitude_min = 100.0
        latitude_max = -100.0
        longitude_min = 100.0
        longitude_max = -100.0
        sample_date_min = '9999-99-99'
        sample_date_max = '0000-00-00'
        
        param_unit_list = set()
        
        # Iterate over rows.
        for target_row in self.target_rows:
            # Don't check filtered rows.
            if target_row.get('remove_row', '') == '<REMOVE>':
                continue
            # Latitude/longitude.
            latitude = float(target_row.get('decimalLatitude', '100.0'))
            longitude = float(target_row.get('decimalLongitude', '100.0'))
            if  latitude != 100.0 and longitude != -100.0:
                latitude_min = min(latitude_min, latitude)
                latitude_max = max(latitude_max, latitude)
                longitude_min = min(longitude_min, longitude)
                longitude_max = max(longitude_max, longitude)
            # Sapling date.
            sample_date = target_row.get('eventDate', '')
            if  sample_date != '':
                sample_date_min = min(sample_date_min, sample_date)
                sample_date_max = max(sample_date_max, sample_date)
            # Parameters.
            parameter = target_row.get('parameter', '')
            unit = target_row.get('unit', '')
            param_unit = ''
            if parameter and unit:
                param_unit = parameter + ' (' + unit + ')'
            elif parameter:
                param_unit = parameter
            if param_unit:
                param_unit_list.add(param_unit)
        
        # Done. 
        self.latitude_min = ''
        self.latitude_max = ''
        self.longitude_min = ''
        self.longitude_max = ''
        self.sample_date_min = ''
        self.sample_date_max = ''
        
        if  latitude_min != 100.0 and latitude_max != -100.0 and \
            longitude_min != 100.0 and longitude_max != -100.0:
            
            self.latitude_min = latitude_min
            self.latitude_max = latitude_max
            self.longitude_min = longitude_min
            self.longitude_max = longitude_max
        
        if sample_date_min != '9999-99-99' and sample_date_max != '0000-00-00':
            self.sample_date_min = sample_date_min
            self.sample_date_max = sample_date_max
        
        self.parameter_list = ', '.join(param_unit_list)
        
    def create_meta_xml(self):
        """ """
        self.meta_xml_rows = []
        meta_xml = dwca_generator.DarwinCoreMetaXml()
        self.meta_xml_rows = meta_xml.create_meta_xml(self.get_event_columns(), 
                                                      self.get_occurrence_columns(), 
                                                      self.get_measurementorfact_columns(),
                                                      )
    
    def create_eml_xml(self, eml_template):
        """ """
        self.eml_xml_rows = []
        
        eml_xml = dwca_generator.DarwinCoreEmlXml()
        self.eml_xml_rows = eml_xml.create_eml_xml(eml_template)
        if len(self.eml_xml_rows) > 1:
            
            for index, xml_row in enumerate(self.eml_xml_rows):
                if 'REPLACE-' in xml_row:                    
                    self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-packageId', 'TODO-PACKAGE-ID')
                    self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-pubDate', str(datetime.datetime.today().date()))
                    self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-westBoundingCoordinate',  str(self.longitude_min))
                    self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-eastBoundingCoordinate',  str(self.longitude_max))
                    self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-northBoundingCoordinate',  str(self.latitude_max))
                    self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-southBoundingCoordinate',  str(self.latitude_min))
                    self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-beginDate-calendarDate',  str(self.sample_date_min))
                    self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-endDate-calendarDate',  str(self.sample_date_max))
                    self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-Parameters',  str(self.parameter_list))
    
    def save_to_archive_file(self, dwca_file_path, eml_template, metadata_dict):
        """ """
        # Darwin Core Archive parts.
        event_content = [] 
        occurrence_content = [] 
        measurementorfact_content = []
           
        # Append headers for Event, Occurrence and Measurementorfact.
        event_content.append('\t'.join(self.get_event_columns()))
        occurrence_content.append('\t'.join(self.get_occurrence_columns())) 
        measurementorfact_content.append('\t'.join(self.get_measurementorfact_columns()))
          
        # Convert from dictionary to row for each item in the list.
        # Event. 
        for row_dict in self.dwca_event:
            row = []
            for column_name in self.get_event_columns():
                row.append(str(row_dict.get(column_name, '')))
            event_content.append('\t'.join(row))
        # Occurrence.
        for row_dict in self.dwca_occurrence:
            row = []
            for column_name in self.get_occurrence_columns():
                row.append(str(row_dict.get(column_name, '')))
            occurrence_content.append('\t'.join(row))
        # Measurementorfact.
        for row_dict in self.dwca_measurementorfact:
            row = []
            for column_name in self.get_measurementorfact_columns():
                row.append(str(row_dict.get(column_name, '')))
            measurementorfact_content.append('\t'.join(row))
                  
        # Create zip archive.
        ziparchive = dwca_generator.ZipArchive(dwca_file_path)
        if len(event_content) > 1:
            ziparchive.appendZipEntry('event.txt', ('\r\n'.join(event_content).encode('utf-8')))
        if len(occurrence_content) > 1:
            ziparchive.appendZipEntry('occurrence.txt', ('\r\n'.join(occurrence_content).encode('utf-8')))
        if len(measurementorfact_content) > 1:
            ziparchive.appendZipEntry('extendedmeasurementorfact.txt', ('\r\n'.join(measurementorfact_content).encode('utf-8')))
        
        if len(self.meta_xml_rows) > 1:
            ziparchive.appendZipEntry('meta.xml', ('\r\n'.join(self.meta_xml_rows).encode('utf-8')))
        
#         # Add eml.xml files to zip.
        if len(self.eml_xml_rows) > 1:
            #
            eml_document = '\r\n'.join(self.eml_xml_rows).encode('utf-8')
            ziparchive.appendZipEntry('eml.xml', eml_document)
     
    def get_event_columns(self):
        """ Implementation of abstract method declared in DwcDatatypeBase. """
    
        return self.resources_object.get_dwc_columns().get('dwc_event_columns', [])
     
    def get_occurrence_columns(self):
        """ Implementation of abstract method declared in DwcDatatypeBase. """
    
        return self.resources_object.get_dwc_columns().get('dwc_occurrence_columns', [])
     
    def get_measurementorfact_columns(self):
        """ Implementation of abstract method declared in DwcDatatypeBase. """
    
        return self.resources_object.get_dwc_columns().get('dwc_emof_columns', [])
    
