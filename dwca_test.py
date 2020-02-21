#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import dwca_generator

if __name__ == "__main__":
    """ """
    import datetime
    print('TEST: Started. ' + str(datetime.datetime.now()))
    print('')
    
#     # Bacterioplankton.
#     print('\n')
#     print('TEST: Bacterioplankton. ' + str(datetime.datetime.now()))
#     print('')
# 
#     # Resource.
#     content_mapper = dwca_generator.DwcaContentMapper()
#     content_mapper.load_from_excel('test_data/resources/dwca_matrix_bacterioplankton.xlsx')
#     species_info = dwca_generator.DwcaSpeciesWorms(taxa_file_path='test_data/resources/translate_dyntaxa_to_worms.txt')
#     
#     # Data.
#     data = dwca_generator.DwcaDataSharkStandard(content_mapper)
#     for dataset_filepath in [
#                 'test_data/SHARK_Bacterioplankton_ABU_2006_UMSC_Bactabund_version_2019-02-14.zip', 
#                 'test_data/SHARK_Bacterioplankton_ABU_2007_UMSC_Bactabund_version_2019-02-14.zip', 
#                 'test_data/SHARK_Bacterioplankton_ABU_2008_UMSC_Bactabund_version_2019-02-14.zip', 
#                 'test_data/SHARK_Bacterioplankton_ABU_2009_UMSC_Bactabund_version_2019-02-14.zip', 
#                 'test_data/SHARK_Bacterioplankton_ABU_2010_UMSC_Bactabund_version_2019-02-14.zip', 
#                 'test_data/SHARK_Bacterioplankton_ABU_2011_UMSC_Bactabund_version_2019-02-14.zip', 
#                 'test_data/SHARK_Bacterioplankton_ABU_2012_UMSC_Bactabund_version_2019-02-14.zip', 
#                 'test_data/SHARK_Bacterioplankton_ABU_2013_UMSC_Bactabund_version_2019-02-14.zip', 
#                 'test_data/SHARK_Bacterioplankton_ABU_2014_UMSC_Bactabund_version_2019-02-14.zip', 
#                 'test_data/SHARK_Bacterioplankton_ABU_2015_UMSC_Bactabund_version_2019-02-14.zip', 
#                 'test_data/SHARK_Bacterioplankton_ABU_2016_UMSC_Bactabund_version_2019-02-14.zip', 
#                 'test_data/SHARK_Bacterioplankton_ABU_2017_UMSC_Bactabund_version_2019-02-14.zip', 
#                 'test_data/SHARK_Bacterioplankton_ABU_2018_UMSC_Bactabund_version_2019-05-28.zip', 
#                 'test_data/SHARK_Bacterioplankton_GR_1991_2015_UMSC_version_2019-02-14.zip', 
#                 'test_data/SHARK_Bacterioplankton_GR_2016_UMSC_version_2019-02-14.zip', 
#                 'test_data/SHARK_Bacterioplankton_GR_2017_UMSC_version_2019-02-14.zip', 
#                 'test_data/SHARK_Bacterioplankton_GR_2018_UMSC_version_2019-05-28.zip', 
#                 'test_data/SHARK_Bacterioplankton_PL_1989_1990_UMSC_version_2019-02-14.zip', 
#                 ]:
#         data.add_shark_dataset(dataset_filepath)
#     data.create_dwca_keys()
#     data.create_dynamic_fields()
#     data.cleanup_data()
# #     data.translate_stations()
# #     data.translate_fields()
#     # Format.
#     dwca_format = dwca_generator.DwcaFormatStandard(data, content_mapper, species_info)
#     dwca_format.create_dwca_parts()
#     dwca_format.extract_metadata()
#     dwca_format.create_meta_xml()
#     dwca_format.create_eml_xml(eml_template = 'templates/eml_bacterioplankton_nat.xml')
#     dwca_format.save_to_archive_file('test_data/SHARK_Bacterioplankton_DwC-A_TEST.zip', '', '')
    
    # Zooplankton.
    print('\n')
    print('TEST: Zooplankton. ' + str(datetime.datetime.now()))
    print('')

    # Resource.
    content_mapper = dwca_generator.DwcaContentMapper()
    content_mapper.load_from_excel('test_data/resources/dwca_matrix_zooplankton.xlsx')
    species_info = dwca_generator.DwcaSpeciesWorms(taxa_file_path='test_data/resources/translate_dyntaxa_to_worms.txt')
    
    source_dir_path = pathlib.Path('test_data')
    file_path_list = []
    
    
    
#     for file_path in source_dir_path.glob('**/SHARK_Zooplankton_*.zip'):
    for file_path in source_dir_path.glob('**/SHARK_Zooplankton_2010*.zip'):
        file_path_list.append(str(file_path))
    
    target_dwca_path = pathlib.Path('test_data/SHARK_Zooplankton_DwC-A_TEST.zip')
    
    # Data.
    data = dwca_generator.DwcaDataSharkStandard(content_mapper, target_dwca_path)
    for dataset_filepath in file_path_list:
        data.add_shark_dataset(dataset_filepath)
    data.create_dwca_keys()
    data.create_dynamic_fields()
    data.cleanup_data()
#     data.translate_stations()
#     data.translate_fields()
    # Format.
    dwca_format = dwca_generator.DwcaFormatStandard(data, content_mapper, species_info, target_dwca_path)
    dwca_format.create_dwca_parts()
    dwca_format.extract_metadata()
    dwca_format.create_meta_xml()
    dwca_format.create_eml_xml(eml_template = 'templates/eml_template.xml')
#     dwca_format.create_eml_xml(eml_template = 'templates/eml_zooplankton.xml')
    dwca_format.save_to_archive_file('test_data/SHARK_Zooplankton_DwC-A_TEST.zip', '', '')
    
#         
#     # Epibenthos NAT.
#     print('\n')
#     print('TEST: Epibenthos NAT. ' + str(datetime.datetime.now()))
#     print('')
#         
#     # Epibenthos REG.
#     print('\n')
#     print('TEST: Epibenthos REG. ' + str(datetime.datetime.now()))
#     print('')
#         
#     # Zoobenthos NAT.
#     print('\n')
#     print('TEST: Zoobenthos NAT. ' + str(datetime.datetime.now()))
#     print('')
#          
#     # Zoobenthos REG.
#     print('\n')
#     print('TEST: Zoobenthos REG. ' + str(datetime.datetime.now()))
#     print('')
#       
#     # Greyseal.
#     print('\n')
#     print('TEST: Greyseal. ' + str(datetime.datetime.now()))
#     print('')
# 
#     # Harbourseal.
#     print('\n')
#     print('TEST: Harbourseal. ' + str(datetime.datetime.now()))
#     print('')
# 
#     # Ringedseal.
#     print('\n')
#     print('TEST: Ringedseal. ' + str(datetime.datetime.now()))
#     print('')
# 
#     # JERICO.
#     print('\n')
#     print('TEST: JERICO. ' + str(datetime.datetime.now()))
#     print('')
# 
#     # JERICO-IFCB.
#     print('\n')
#     print('TEST: JERICO-IFCB. ' + str(datetime.datetime.now()))
#     print('')
    
    missing_taxa = species_info.get_missing_taxa_list()
    if len(missing_taxa) > 0:
        print('')
        print('Missing taxa in "', species_info.taxa_file_path, '"')
        for taxa in missing_taxa:
            print('- ',taxa)
    
    
    print('')
    print('TEST: Finished. ' + str(datetime.datetime.now()))

