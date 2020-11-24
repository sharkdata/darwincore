#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019-present SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import copy
import pathlib
import datetime

import dwca_generator

class DwcaFormatStandard(object):
    """ """
    def __init__(self, data=None, dwca_gen_config=None, species_info=None):
        """ Darwin Core Archive Format base class. """
        
        self.target_dwca_path = pathlib.Path(dwca_gen_config.dwca_target)
        self.data_object = data
        self.dwca_gen_config = dwca_gen_config
        self.species_info_object = species_info
        self.worms_info_object = None
        #
        self._taxa_lookup_dict = {}
        #
        self.clear()
    
    def clear(self):
        """ """
        self.source_rows = []
        self.dwca_event = [] 
        self.dwca_occurrence = [] 
        self.dwca_measurementorfact = [] 
     
    def create_dwca_parts(self):
        """ """
        self.source_rows = self.data_object.get_data_rows()
        #
        self.create_dwca_event()
        self.create_dwca_occurrence()
        self.create_dwca_measurementorfact()
    
    def create_dwca_event(self):
        """ """
        # Create control dictionary.
        event_keys = self.dwca_gen_config.dwca_keys["eventTypeKeys"]["event"]
        dwca_node_names = [event_dict["eventType"] for event_dict in event_keys]
        event_control_dict = {}
        for index, dwca_node_name in enumerate(dwca_node_names):
            event_control_dict[dwca_node_name] = {}
            event_control_dict[dwca_node_name]['used_key_list'] = set() # To avoid duplicates.
            event_control_dict[dwca_node_name]['dwc_key_name'] = event_keys[index]['keyName']
        
        # Process all data rows.
        for source_row in self.source_rows:
            # Check if marked for removal.
            if source_row.get('remove_row', '') == '<REMOVE>':
                continue
            # Iterate over nodes.
            for dwca_node_name in dwca_node_names:
                # Current row in control dictionary.
                control_dict = event_control_dict[dwca_node_name]
                # Get keys.
                node_key = source_row.get(control_dict['dwc_key_name'], '')
                # parent_node_key = source_row.get(control_dict['dwc_event_key_name'], '')
                # Create event row.
                if node_key and (node_key not in control_dict['used_key_list']):
                    control_dict['used_key_list'].add(node_key)
                    #
                    event_dict = {}
                    # Add basics.
                    event_dict['id'] = node_key
                    event_dict['type'] = dwca_node_name
                    # event_dict['eventID'] = node_key
                    # event_dict['parentEventID'] = parent_node_key

                    event_content_list = self.dwca_gen_config.field_mapping["dwcaEventContent"]
                    for event_content in event_content_list:
                        if dwca_node_name != event_content.get("eventType", ""):
                            continue
                        # Add content.
                        self.add_content(event_content, source_row, event_dict)
                        # Append event row content.
                        self.dwca_event.append(event_dict) 
    
    def create_dwca_occurrence(self):
        """ """
        # Create control dictionary.
        occurrence_keys = self.dwca_gen_config.dwca_keys["eventTypeKeys"]["occurrence"]
        dwca_node_names = [occurrence_key["eventType"] for occurrence_key in occurrence_keys]
        occurrence_control_dict = {}
        for index, dwca_node_name in enumerate(dwca_node_names):
            occurrence_control_dict[dwca_node_name] = {}
            occurrence_control_dict[dwca_node_name]['used_key_list'] = set() # To avoid duplicates.
            occurrence_control_dict[dwca_node_name]['dwc_key_name'] = occurrence_keys[index]['keyName']
        
        # Process all data rows.
        for source_row in self.source_rows:
            # Check if marked for removal.
            if source_row.get('remove_row', '') == '<REMOVE>':
                continue
            # Iterate over nodes.
            for dwca_node_name in dwca_node_names:
                if dwca_node_name not in occurrence_control_dict:
                    continue
                # Current row in control dictionary.
                control_dict = occurrence_control_dict[dwca_node_name]
                # Get keys.
                node_key = source_row.get(control_dict['dwc_key_name'], '')
                # event_node_key = source_row.get(control_dict['dwc_event_key_name'], '')
                # Create event row.
                if node_key and (node_key not in control_dict['used_key_list']):
                    control_dict['used_key_list'].add(node_key)
                    #
                    occurrence_dict = {}
                    # Add basics.
                    # occurrence_dict['id'] = event_node_key
                    # occurrence_dict['eventID'] = event_node_key
                    occurrence_dict['occurrenceID'] = node_key

                    content_list = self.dwca_gen_config.field_mapping["dwcaOccurrenceContent"]
                    for content in content_list:
                        if dwca_node_name != content.get("eventType", ""):
                            continue
                        # Add content.
                        self.add_content(content, source_row, occurrence_dict)

                        # # Add taxa info.
                        # taxa_info_dict = self.species_info_object.get_info_as_dwc_dict(source_dict=source_row)
                        # occurrence_dict.update(taxa_info_dict)
                        # #
                        # scientific_name = occurrence_dict.get('scientificName', '')
                        # if scientific_name:
                        #     # Translate values.
                        #     for key in self.resources_object.get_translate_from_source_keys():
                        #         value = occurrence_dict.get(key, '')
                        #         if value:
                        #             new_value = self.resources_object.get_translate_from_source(key, value)
                        #             if value != new_value:
                        #                 occurrence_dict[key] = new_value

                        # Append occurrence row content.
                        self.dwca_occurrence.append(occurrence_dict)

    def create_dwca_measurementorfact(self):
        """ """
        # For checking for duplicates.
        used_mof_occurrence_key_list = set()
        duplicate_row_number = 0

        # Create control dictionary.
        emof_keys = self.dwca_gen_config.dwca_keys["eventTypeKeys"]["emof"]
        dwca_node_names = [event_dict["eventType"] for event_dict in emof_keys]
        emof_control_dict = {}
        for index, dwca_node_name in enumerate(dwca_node_names):
            emof_control_dict[dwca_node_name] = {}
            emof_control_dict[dwca_node_name]['used_key_list'] = set() # To avoid duplicates.
            emof_control_dict[dwca_node_name]['dwc_key_name'] = emof_keys[index]['keyName']
            emof_control_dict[dwca_node_name]['dwc_event_key_name'] = emof_keys[index]['keyName']

        # Process all data rows.
        for source_row in self.source_rows:
            # Check if marked for removal.
            if source_row.get('remove_row', '') == '<REMOVE>':
                continue
            # Check for duplicates.
            emof_param_unit_id = source_row.get('emof_param_unit_id', '')
            if emof_param_unit_id and (emof_param_unit_id not in used_mof_occurrence_key_list):
                used_mof_occurrence_key_list.add(emof_param_unit_id)

                # Iterate over nodes.
                for dwca_node_name in dwca_node_names:
                    if dwca_node_name not in emof_control_dict:
                        continue
                    # Current row in control dictionary.
                    control_dict = emof_control_dict[dwca_node_name]
                    # Get keys.
                    event_node_key = source_row.get(control_dict['dwc_event_key_name'], '')
                    # Create event row.
    #                 if node_key and (node_key not in control_dict['used_key_list']):
    #                     control_dict['used_key_list'].add(node_key)
                    #
                    emof_dict = {}
                    # Add basics.
                    emof_dict['id'] = event_node_key
                    emof_dict['eventID'] = event_node_key
                    
                    content_list = self.dwca_gen_config.field_mapping["dwcaOccurrenceContent"]
                    for content in content_list:
                        if dwca_node_name != content.get("eventType", ""):
                            continue

                            # Add content.
                            self.add_content(content, source_row, occurrence_dict)

                    if dwca_node_name == 'occurrence':
                        occurrence_key = source_row.get('occurrence_key', '')
                        scientific_name = source_row.get('scientific_name', '')
                        if occurrence_key and scientific_name:
                            emof_dict['occurrenceID'] = occurrence_key
                        
                        parameter = source_row.get('parameter', '')
                        value = source_row.get('value', '')
                        unit = source_row.get('unit', '')
                        if parameter:
                            emof_dict['measurementType'] = parameter
                            emof_dict['measurementValue'] = value
                            emof_dict['measurementUnit'] = unit
        #                     measurementorfact_dict['measurementAccuracy'] = ''
        #                     measurementorfact_dict['measurementDeterminedDate'] = source_row.get('measurementDeterminedDate', '')
        #                     measurementorfact_dict['measurementDeterminedBy'] = source_row.get('measurementDeterminedBy', '')
        #                     measurementorfact_dict['measurementMethod'] = source_row.get('measurementMethod', '') # TODO: method_reference_code
        #                     measurementorfact_dict['measurementRemarks'] = source_row.get('measurementRemarks', '')
                                    
                            # Measurement identifiers. NERC vocabular.
                            if parameter == 'Water depth':
                                emof_dict['measurementTypeID'] = 'http://vocab.nerc.ac.uk/collection/P01/current/MAXWDIST/'
                            if unit == 'm':
                                emof_dict['measurementUnitID'] = 'http://vocab.nerc.ac.uk/collection/P06/current/ULAA/'
                            elif unit == 'cells/l':
                                emof_dict['measurementUnitID'] = 'http://vocab.nerc.ac.uk/collection/P06/current/UCPL/'
                                    
                            # # Translate values.
                            # for key in self.resources_object.get_translate_from_source_keys():
                            #     value = emof_dict.get(key, '')
                            #     if value:
                            #         new_value = self.resources_object.get_translate_from_source(key, value)
                            #         if value != new_value:
                            #             emof_dict[key] = new_value
                            # Append.
                            self.dwca_measurementorfact.append(emof_dict) 
                    # else: 

                    #     # Not occurrence.
                    #     # Get key.
                    #     event_node_key = source_row.get(control_dict['dwc_key_name'], '')
                    #     # Create event row.
                    #     if event_node_key and (event_node_key not in control_dict['used_key_list']):
                    #         control_dict['used_key_list'].add(event_node_key)
                            
                    #         for key, (param, unit) in emof_control_dict[event_node_name]['emof_extra_params'].items(): 
                    #             value = str(source_row.get(key, ''))
                    #             if value: 
                    #                 emof_dict_2 = dict(emof_dict)
                    #                 emof_dict_2['measurementType'] = param 
                    #                 emof_dict_2['measurementValue'] = value 
                    #                 emof_dict_2['measurementUnit'] = unit
                                    
                    #                 # Measurement identifiers. NERC vocabular.
                    #                 if param == 'Water depth':
                    #                     emof_dict_2['measurementTypeID'] = 'http://vocab.nerc.ac.uk/collection/P01/current/MAXWDIST/'
                    #                 if unit == 'm':
                    #                     emof_dict_2['measurementUnitID'] = 'http://vocab.nerc.ac.uk/collection/P06/current/ULAA/'
                    #                 elif unit == 'cells/l':
                    #                     emof_dict_2['measurementUnitID'] = 'http://vocab.nerc.ac.uk/collection/P06/current/UCPL/'
                                    
                    #                 # Translate values.
                    #                 for key in self.resources_object.get_translate_from_source_keys():
                    #                     value = emof_dict_2.get(key, '')
                    #                     if value:
                    #                         new_value = self.resources_object.get_translate_from_source(key, value)
                    #                         if value != new_value:
                    #                             emof_dict_2[key] = new_value
                    #                 # Append.
                    #                 self.dwca_measurementorfact.append(emof_dict_2)

            else:
                # For checking for duplicates.
                duplicate_row_number += 1
                if duplicate_row_number < 100:
                    try:
                        print('DEBUG: Duplicates: emof_param_unit_id: ' + str(emof_param_unit_id))
                    except Exception as e:
                        print('DEBUG: Exception: ' + str(e))
                elif duplicate_row_number == 100:
                    print('DEBUG: MAX LIMIT OF 100 LOG ROWS.')
        # Finally.
        if duplicate_row_number > 0:
            print('DEBUG: Number of duplicates found: ', duplicate_row_number)

    def add_content(self, content, source_row, result_dict):
        """ """
        for term in content.get("dwcTerms", []):
            # print(term)
            # print(content["dwcTerms"][term])
            term_dict = content["dwcTerms"][term]
            if not term_dict:
                continue

            if "default" in term_dict:
                value = term_dict["default"]
                if value:
                    result_dict[term] = value
            #
            if "text" in term_dict:
                value = term_dict["text"]
                if value:
                    result_dict[term] = value
            elif "sourceKey" in term_dict:
                source_key = term_dict["sourceKey"]
                value = source_row.get(source_key, '')
                if value:
                    result_dict[term] = value
            elif "dwcaKey" in term_dict:
                dwca_key = term_dict["dwcaKey"]
                value = source_row.get(dwca_key, '')
                if value:
                    result_dict[term] = value
            
            elif "dynamic" in term_dict:
                source_key = term_dict["dynamic"]
                value = source_row.get(source_key, '')
                # TODO:
                if value:
                    result_dict[term] = value

                # event_control_dict[event_node_name]['dynamic_field_list'] = []
                # #
                # for row_dict in self.resources_object.field_mapping:
                #     dwc_category = row_dict.get('dwc_category', '')
                #     dwc_event_node = row_dict.get('dwc_event_node', '')
                #     if dwc_category == 'event':
                #         if dwc_event_node == event_node_name:
                            
                #             text_field = row_dict.get('text', '')
                #             source_field = row_dict.get('source_field', '')
                #             dwc_field = row_dict.get('dwc_field', '')
                #             if dwc_field:
                #                 if text_field:
                #                     event_control_dict[event_node_name]['text_from_to_list'].append((text_field, dwc_field))
                #                 if source_field:
                #                     event_control_dict[event_node_name]['field_from_to_list'].append((source_field, dwc_field))

                # # Add dynamicProperties.
                # for dynamic_field_key in used_dynamic_field_key_list:
                #     if 'event<+>' + event_node_name + '<+>' in dynamic_field_key:
                #         # Remove dwc_event_node part from key.
                #         new_key = dynamic_field_key.replace('event<+>' + event_node_name + '<+>', '')
                #         value = source_row.get(dynamic_field_key, '')
                #         if value:
                #             event_dict[new_key] = value
                # #
                # # Translate values.
                # for key in self.resources_object.get_translate_from_dwc_keys():
                #     value = event_dict.get(key, '')
                #     if value:
                #         new_value = self.resources_object.get_translate_from_dwc(key, value)
                #         if value != new_value:
                #             event_dict[key] = new_value


    def extract_metadata(self):
        """ """
        latitude_min = 100.0
        latitude_max = -100.0
        longitude_min = 100.0
        longitude_max = -100.0
        sample_date_min = '9999-99-99'
        sample_date_max = '0000-00-00'
        
        param_unit_list = set()
        
        # Iterate over event rows.
        for event_row in self.dwca_event:
            # Don't check filtered rows.
            if event_row.get('remove_row', '') == '<REMOVE>':
                continue
            # Latitude/longitude.
            latitude = float(event_row.get('decimalLatitude', '100.0'))
            longitude = float(event_row.get('decimalLongitude', '100.0'))
            if  latitude != 100.0 and longitude != -100.0:
                latitude_min = min(latitude_min, latitude)
                latitude_max = max(latitude_max, latitude)
                longitude_min = min(longitude_min, longitude)
                longitude_max = max(longitude_max, longitude)
            # Sampling date.
            sample_date = event_row.get('eventDate', '')
            if  sample_date != '':
                sample_date_min = min(sample_date_min, sample_date)
                sample_date_max = max(sample_date_max, sample_date)
        
        # Iterate over emof rows.
        for emof_row in self.dwca_measurementorfact:
            # Parameters and units.
            parameter = emof_row.get('measurementType', '')
            unit = emof_row.get('measurementUnit', '')
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
    
    def create_eml_xml(self, eml_content):
        """ """
        self.eml_xml_rows = []
        

        self.eml_xml_rows = eml_content


        # eml_xml = dwca_generator.DarwinCoreEmlXml(resources = self.resources_object, target_dwca_path=self.target_dwca_path)
        # self.eml_xml_rows = eml_xml.create_eml_xml(eml_template)
        # if len(self.eml_xml_rows) > 1:
            
        #     for index, xml_row in enumerate(self.eml_xml_rows):
        #         if 'REPLACE-' in xml_row:                    
        #             self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-packageId', 'TODO-PACKAGE-ID')
        #             self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-pubDate', str(datetime.datetime.today().date()))
        #             self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-westBoundingCoordinate',  str(self.longitude_min))
        #             self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-eastBoundingCoordinate',  str(self.longitude_max))
        #             self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-northBoundingCoordinate',  str(self.latitude_max))
        #             self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-southBoundingCoordinate',  str(self.latitude_min))
        #             self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-beginDate-calendarDate',  str(self.sample_date_min))
        #             self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-endDate-calendarDate',  str(self.sample_date_max))
        #             self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-Parameters',  str(self.parameter_list))
                    
        #             self.eml_xml_rows[index] = self.eml_xml_rows[index].replace('REPLACE-additionalMetadata-metadata-gbif-dateStamp',  
        #                                                                         str(datetime.datetime.now()))
    
    def save_to_archive_file(self):
        """ """
        # Darwin Core Archive parts.
        event_content = [] 
        occurrence_content = [] 
        measurementorfact_content = []
           
        # Append headers for Event, Occurrence and Measurementorfact.
        event_columns = self.get_event_columns()
        event_content.append('\t'.join(event_columns))
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
        ziparchive = dwca_generator.ZipArchive(self.target_dwca_path)
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
            # eml_document = '\r\n'.join(self.eml_xml_rows).encode('utf-8')
            eml_document = self.eml_xml_rows.encode('utf-8')
            ziparchive.appendZipEntry('eml.xml', eml_document)
     
    def get_event_columns(self):
        """ Implementation of abstract method declared in DwcDatatypeBase. """
        # return self.resources_object.get_dwc_columns().get('dwc_event_columns', [])
        event_columns = self.dwca_gen_config.field_mapping.get('dwcaEventColumns', [])
        return event_columns
     
    def get_occurrence_columns(self):
        """ Implementation of abstract method declared in DwcDatatypeBase. """
        # return self.resources_object.get_dwc_columns().get('dwc_occurrence_columns', [])
        occurrence_columns = self.dwca_gen_config.field_mapping.get('dwcaOccurrenceColumns', [])
        return occurrence_columns
     
    def get_measurementorfact_columns(self):
        """ Implementation of abstract method declared in DwcDatatypeBase. """
        # return self.resources_object.get_dwc_columns().get('dwc_emof_columns', [])
        emof_columns =  self.dwca_gen_config.field_mapping.get('dwcaEmofColumns', [])
        return emof_columns


