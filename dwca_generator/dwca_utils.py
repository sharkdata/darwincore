#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import codecs
import locale
import zipfile
import time
import datetime
import pytz
# from django.core.exceptions import ObjectDoesNotExist

excel_support = True 
try: import openpyxl 
except: excel_support = False 

xml_support = True
try: from lxml import etree 
except: xml_support = False

############# from django.core.exceptions import ObjectDoesNotExist
############# import app_resources.models as resources_models

""" """
def singleton(cls):
    """ """
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


def create_extra_key(row_dict, key_list):
    """ """
    key_string = ''
    try:
#            key_list = [str(row_dict.get(item, '')) for item in key_columns if row_dict.get(item, False)]
        value_list = []
        for key in key_list:
            value = str(row_dict.get(key, '')) 
            if value:
                value_list.append(key + ':' + value.replace(',', '.'))
        key_string = ','.join(value_list)
    except:
        key_string = 'ERROR: Failed to generate key-string'
    # Replace swedish characters.
    key_string = key_string.replace('Å', 'A')
    key_string = key_string.replace('Ä', 'A')
    key_string = key_string.replace('Ö', 'O')
    key_string = key_string.replace('å', 'a')
    key_string = key_string.replace('ä', 'a')
    key_string = key_string.replace('ö', 'o')
    key_string = key_string.replace('µ', 'u')
    #
    return key_string


def is_daylight_savings_time(date_str, zone_name='Europe/Stockholm'):
    """ Returns True if DST=Daylight Savings Time. """
    try:
        localtime = pytz.timezone(zone_name)
        datetime_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        localized_date = localtime.localize(datetime_date)
        return bool(localized_date.dst())
    except:
        return False

@singleton
class ExportFilter():
    """ """
    def __init__(self):
        """ """
        self.filter_keep_dict = {}
        self.filter_remove_dict = {}
    
    def get_filter_keep_list(self, internal_key):
        """ """
        if internal_key in self.filter_keep_dict.keys():
            return self.filter_keep_dict[internal_key]
        else:
            return []
    
    def get_filter_remove_list(self, internal_key):
        """ """
        if internal_key in self.filter_remove_dict.keys():
            return self.filter_remove_dict[internal_key]
        else:
            return []
    
    def load_export_filter(self, resource_name):
        """ """
        self.filter_keep_dict = {}
        self.filter_remove_dict = {}
        #
        resource = None
#         try: resource = resources_models.Resources.objects.get(resource_name = resource_name)
#         except ObjectDoesNotExist: resource = None
#         if resource:
#             data_as_text = resource.file_content # .encode('cp1252')
#             for index, row in enumerate(data_as_text.split('\n')):
        #
#         filter_file_path = pathlib.Path('D:/arnold/4_sharkdata\sharkdata_ftp/resources/export_ices_filters.txt')
        filter_file_path = pathlib.Path('D:/arnold/42_sharkdata_py3/test_data/SHARKdata_resources/export_ices_filters.txt')
        
        with filter_file_path.open('r') as filter_file:
        #
            header = []
            for index, row in enumerate(filter_file):
                row = [item.strip() for item in row.split('\t')]
                if index == 0:
                    header = row
                else:
                    # Keep filter.
                    if len(row) >= 2:
                        internal_key = row[0]
                        keep_value = row[1]
                        if keep_value:
                            if internal_key not in self.filter_keep_dict.keys():
                                self.filter_keep_dict[internal_key] = []
                            #
                            self.filter_keep_dict[internal_key].append(keep_value)
                    # Remove filter.
                    if len(row) >= 3:
                        internal_key = row[0]
                        remove_value = row[2]
                        if remove_value:
                            if internal_key not in self.filter_remove_dict.keys():
                                self.filter_remove_dict[internal_key] = []
                            #
                            self.filter_remove_dict[internal_key].append(remove_value)

@singleton
class TranslateTaxa():
    """ """
    def __init__(self):
        """ """
        self.translate_taxa_dict = {}
        self.missing_taxa_list = []
    
    def get_translated_aphiaid_and_name(self, scientific_name):
        """ """
        if scientific_name in self.translate_taxa_dict:
            return self.translate_taxa_dict[scientific_name]
        #
        if scientific_name not in self.missing_taxa_list:
            self.missing_taxa_list.append(scientific_name)
        #    
#         return ('', '')
        return {}
    
    def get_missing_taxa_list(self):
        """ """
        return self.missing_taxa_list
    
    def load_translate_taxa(self, resource_name):
        """ """
        self.translate_taxa_dict = {}
        self.missing_taxa_list = []
        #
        
#         translate_file_path = pathlib.Path('D:/arnold/4_sharkdata\sharkdata_ftp/resources/species_2018_updated_2018-01-24.txt')
#         translate_file_path = pathlib.Path('D:/arnold/4_sharkdata\sharkdata_ftp/resources/translate_dyntaxa_to_worms.txt')
        translate_file_path = pathlib.Path('D:/arnold/42_sharkdata_py3/data_in/resources/translate_dyntaxa_to_worms.txt')
        with translate_file_path.open('r') as translate_file:
            for index, row in enumerate(translate_file):
                row = [item.strip() for item in row.split('\t')]
                if index == 0:
                    # dyntaxa_scientific_name    worms_valid_aphia_id    worms_valid_name
                    header = row
                else:
                    if len(row) >= 2:
                        row_dict = dict(zip(header, row))
                        self.translate_taxa_dict[row_dict.get('scientific_name', '')] = row_dict
#                             (row_dict.get('worms_valid_aphia_id', ''), 
#                              row_dict.get('worms_valid_name', ''))

#         resource = None
#         try: resource = resources_models.Resources.objects.get(resource_name = resource_name)
#         except ObjectDoesNotExist: resource = None
#         #
#         if resource:
#             data_as_text = resource.file_content # .encode('cp1252')
#             header = []
#             for index, row in enumerate(data_as_text.split('\n')):
#                 row = [item.strip() for item in row.split('\t')]
#                 if index == 0:
#                     # Supposed to be at least 'dyntaxa_scientific_name', 'worms_aphia_id', 'ices_rlist'.
#                     
#                     # dyntaxa_scientific_name    worms_valid_aphia_id    worms_valid_name
#                     
#                     header = row
#                 else:
#                     if len(row) >= 2:
#                         row_dict = dict(zip(header, row))
#                         self.translate_taxa_dict[row_dict.get('dyntaxa_scientific_name', '')] = \
#                             (row_dict.get('worms_valid_aphia_id', ''), row_dict.get('ices_rlist', ''))




                            
# class SpeciesWormsInfo():
#     """ 
#     """
#     def __init__(self):
#         """ """
#         self.clear()
#         self.species_dict = {}
#          
#     def clear(self):
#         """ """
#         self.species_dict = {}
#           
#     def getTaxonInfoDict(self, scientific_name):
#         """ """
#         return self.species_dict.get(scientific_name, None)
#           
#     def loadSpeciesFromResource(self):
#         """ """
#         self.clear()
#         #
#         resource = None
#         try:
#             resource = resources_models.Resources.objects.get(resource_name = 'taxa_worms_info')
#         except ObjectDoesNotExist:
#             resource = None
#         if resource:
#             header_row = None
# #             data_as_text = resource.file_content.encode('cp1252')
#             data_as_text = resource.file_content
#             for index, row in enumerate(data_as_text.split('\n')):
#                 if index == 0:
#                     header_row = [item.strip() for item in row.split('\t')]
#                 else:
#                     row = [item.strip() for item in row.split('\t')]
#                     row_dict = dict(zip(header_row, row))
#                     if row_dict.get('Scientific name', None):
#                         taxon_dict = {}
#                         taxon_dict['aphia_id'] = row_dict.get('WORMS AphiaID', '')
#                         taxon_dict['kingdom'] = row_dict.get('WORMS Kingdom', '')
#                         taxon_dict['phylum'] = row_dict.get('WORMS Phylum', '')
#                         taxon_dict['class'] = row_dict.get('WORMS Class', '')
#                         taxon_dict['order'] = row_dict.get('WORMS Order', '')
#                         taxon_dict['family'] = row_dict.get('WORMS Family', '')
#                         taxon_dict['genus'] = row_dict.get('WORMS Genus', '')
# #                         taxon_dict['specific_epithet'] = row_dict.get('WORMS specific_epithet', '')
#                         taxon_dict['authority'] = row_dict.get('WORMS Authority', '')
#                         #
#                         if taxon_dict['aphia_id']:
#                             self.species_dict[row_dict['Scientific name']] = taxon_dict
                    
         
class Dataset():
    """ 
    Contains header and rows for the table based dataset. 
    Metadata is handled as a key/value dictionary. (TODO: NOT IMPLEMENTED...)
    """

    def __init__(self):
        """ """
        self.clearData()
        self.clearMetadata()
        
    def clearData(self):
        """ """
        self.data_header = None
        self.data_rows = []
         
    def clearMetadata(self):
        """ """
        self.metadata_dict = {}
        
    def loadDataFromZipFile(self, 
                            zip_file_name,
                            zip_entry = 'shark_data.txt', 
                            dataset_dir_path = None, 
                            encoding = None, 
                            header_row = 0, 
                            data_rows_from = 1):
        """ """
        self.clearData()
        # Check.
        if zip_file_name == None:
            raise UserWarning("Zip file name is missing.")
        # Get encoding if not specified.
        if not encoding:
            encoding = locale.getpreferredencoding()
        #
        if dataset_dir_path:
            zip_file_path = pathlib.Path(dataset_dir_path, zip_file_name)
        else:
            zip_file_path = zip_file_name

        # Read data.
        zip_file = None
        try:
            zip_file = zipfile.ZipFile(zip_file_path, 'r') 
            #
            fieldseparator = None
            # Iterate over rows in file.            
            for rowindex, row in enumerate(zip_file.open(zip_entry).readlines()):
                # Convert to unicode.
                row = str(row, encoding, 'strict')
                if rowindex == header_row:
                    # Header.
                    fieldseparator = self.getSeparator(row)
                    row = [item.strip() for item in row.split(fieldseparator)]
                    self.data_header =row
                elif rowindex >= data_rows_from:
                    # Row.
                    if len(row.strip()) == 0: 
                        continue # Don't add empty rows.
                    row = [item.strip() for item in row.split(fieldseparator)]
                    self.data_rows.append(row)             
        #
        finally:
            if zip_file: zip_file.close()

    def loadDataFromTextFile(self, 
                             dataset_file_name, 
                             dataset_dir_path = None, 
                             encoding = None, 
                             header_row = 0, 
                             data_rows_from = 1):
        """ """
        self.clearData()
        # Check.
        if dataset_file_name == None:
            raise UserWarning("File name is missing.")
        # Get encoding if not specified.
        if not encoding:
            encoding = locale.getpreferredencoding()
        #
        if dataset_dir_path:
            dataset_file_path = pathlib.Path(dataset_dir_path, dataset_file_name)
        else:
            dataset_file_path = dataset_file_name

        # Read file.
        infile = None
        try:
            infile = open(dataset_file_path, 'r')
            fieldseparator = None
            # Iterate over rows in file.            
            for rowindex, row in enumerate(infile):
                # Convert to unicode.
                row = str(row, encoding, 'strict')
                if rowindex == header_row:
                    # Header.
                    fieldseparator = self.getSeparator(row)
                    row = [item.strip() for item in row.split(fieldseparator)]
                    self.data_header =row
                elif rowindex >= data_rows_from:
                    # Row.
                    if len(row.strip()) == 0: 
                        continue # Don't add empty rows.
                    row = [item.strip() for item in row.split(fieldseparator)]
                    self.data_rows.append(row)             
        #
        finally:
            if infile: infile.close()

    def writeDataToTextFile(self, 
                            file_name,
                            encoding = None,
                            field_separator = '\t',
                            row_separator = '\r\n'):
        """ """
        # Check.
        if file_name == None:
            raise UserWarning("File name is missing.")
        # Get encoding if not specified.
        if not encoding:
            encoding = locale.getpreferredencoding()
        # Write to file.
        outfile = None
        try:
            outfile = codecs.open(file_name, mode = 'w', encoding = encoding)
            # Header.
            outfile.write(field_separator.join(map(str, self.data_header)) + row_separator)
            # Rows.
            for row in self.data_rows:
                outfile.write(field_separator.join(map(str, row)) + row_separator)
        except (IOError, OSError):
            raise UserWarning("Failed to write to text file: " + file_name)
        finally:
            if outfile: outfile.close()

    def getSeparator(self, row):
        """ Check the header row for used delimiter. """
        if '\t' in row: return '\t' # First alternative.
        elif ';' in row: return ';'# Second alternative. 
        else: return '\t' # Default alternative.
        
    def loadDataFromExcel(self, 
                          file_name,
                          sheet_name = None, 
                          header_row = 0, 
                          data_rows_from = 1, 
                          data_rows_to = None): # None = read all.
        """ """
        if not excel_support:
            raise UserWarning("Excel not supported. Please install openpyxl")
        if file_name == None:
            raise UserWarning("File name is missing.")
        try:
            workbook = openpyxl.load_workbook(file_name, use_iterators = True) # Supports big files.
            if workbook == None:
                raise UserWarning("Can't read Excel (.xlsx) file.")
            worksheet = None
            if sheet_name:
                # 
                if sheet_name in workbook.get_sheet_names():
                    worksheet = workbook.get_sheet_by_name(name = sheet_name)
                else:
                    raise UserWarning("Excel sheet " + sheet_name + " not available.")      
            else:
                # Use the first sheet if not specified.
                worksheet = workbook.get_sheet_by_name(name = workbook.get_sheet_names()[0])
            #
            header = []
            for rowindex, row in enumerate(worksheet.iter_rows()): ### BIG.
                if data_rows_to and (rowindex > data_rows_to):
                    break # Break loop if data_row_to is defined and exceeded.
                elif rowindex == header_row:
                    for cell in row:
                        value = cell.internal_value
                        if value == None:
                            header.append('')
                        else:
                            header.append(str(value).strip())
                    self.data_header = header
                elif rowindex >= data_rows_from:
                    newrow = []
                    for cell in row:
                        value = cell.internal_value
                        if value == None:
                            newrow.append('')
                        else:
                            newrow.append(str(value).strip())
                    self.data_rows.append(newrow)
        #  
        except Exception:
            raise UserWarning("Can't read Excel file. File name: " + file_name)
 
    def writeDataToExcel(self, file_name):
        """ """
        if not excel_support:
            raise UserWarning("Excel not supported. Please install openpyxl")
        if file_name == None:
            raise UserWarning("File name is missing.")
        try:
            workbook =  openpyxl.Workbook(optimized_write = True)  # Supports big files.
            worksheet = workbook.create_sheet()
            # Header.
            worksheet.append(self.data_header)
            # Rows.
            for row in self.data_rows:
                worksheet.append(row)
            # Save to file.   
            workbook.save(file_name)
        #
        except (IOError, OSError):
            raise UserWarning("Failed to write to file: " + file_name)


class ZipArchive():
    """ """
    def __init__(self, zip_file_name):
        """ """
        self._filepathname = pathlib.Path(zip_file_name)
        # Delete old version, if exists.
        if self._filepathname.exists():
            self._filepathname.unlink() # Unlink = remove.
            time.sleep(0.5) # Time needed to remove the file.
 
    def appendZipEntry(self, zip_entry_name, content):
        """ """
        ziparchive = None
        try:
            ziparchive = zipfile.ZipFile(self._filepathname, 'a', zipfile.ZIP_DEFLATED) # Append. 
            ziparchive.writestr(zip_entry_name, content)
        finally:
            if ziparchive:
                ziparchive.close()

    def appendFileAsZipEntry(self, zip_entry_name, file_path):
        """ """
        ziparchive = None
        try:
            ziparchive = zipfile.ZipFile(self._filepathname, 'a', zipfile.ZIP_DEFLATED) # Append. 
            ziparchive.write(file_path, zip_entry_name)
        finally:
            if ziparchive:
                ziparchive.close()


class XmlFileCreator(object):
    """ Creates XML file from XSLT template. """
    def __init__(self):
        """ """
        self.xslt_file_path = pathlib.Path('settings', 'shark_metadata_iso_19139.xslt')

    def metadataToIso19139(self, metadata_as_text):
        """ Metadata to XML. """
        metadata_as_xml = self._metadataTextToXml(metadata_as_text, rootname = "SharkMetadata")
        print('\n\n' + 'Metadata as XML: ' + etree.tostring(metadata_as_xml))
         
        # Transform.
        xsl_file = str(pathlib.Path(self.xslt_file_path)).replace('\\','/')
        xsl = etree.parse(xsl_file)
        xslt = etree.XSLT(xsl)
        metadata_as_iso19139 =  xslt(metadata_as_xml)
        #
        print('\n\n' + str(metadata_as_iso19139))
        return metadata_as_iso19139
     
    def _metadataTextToXml(self, metadata_as_text, rootname):
        """ Transform a metadata record to a flat XML string. """
     
        metadata_dict = {}
        for row in metadata_as_text.split('\r\n'):
            if ':' in row:
                parts = row.split(':', 1) # Split on first occurence.
                key = parts[0].strip()
                value = parts[1].strip()
                metadata_dict[key] = value
        
        root = etree.Element(rootname)
     
        for key in metadata_dict.keys():
            
            col=key
            dat=''
            try:
                dat=str(metadata_dict[key]) # may need to be careful of unicode encoding issues when reading data from Excel
            except:
                ####dat=str(metadata_dict[key.decode('cp1252', 'replace')])
                dat=str('ERROR when decoding.')
                
            # TODO: Split on '#' to create lists. Used for lists of Parameters/units.
        
            if '#' not in key:

                child=etree.SubElement(root,col)
                child.text=dat

        return root

        # EXAMPLE CODE:
        # 
        # <root atr="100">
        #   text1
        #   <child atr="atr">
        #     <superchild atr="">sctext1</superchild>
        #     tail1
        #     tail2
        #   </child>
        #   tail
        #   <child atr="">text</child>
        # </root>
        # 
        # root = Element('root', atr=str(100))
        # root.text = 'text1'
        # child = SubElement(root, 'child', atr="atr")
        # superchild = SubElement(root, 'superchild', atr="" if value is None else value)
        # superchild.text = 'sctext1'
        # superchild.tail = 'tail1'
        # superchild.tail += 'tail2'
        # child.tail = 'tail'
        # child = SubElement(root, 'child', atr="")
        # child.text = 'text'

        

