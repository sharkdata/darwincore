#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import dwca_generator

if __name__ == "__main__":
    """ """
    import datetime
    print('TEST: Started. ' + str(datetime.datetime.now()))
    print('')
    
    # Zoobenthos NAT.
    print('\n')
    print('TEST: Zoobenthos NAT. ' + str(datetime.datetime.now()))
    print('')
    
    # Resource.
    resources = dwca_generator.DwcaResources()
    resources.load_from_excel('test_data/dwca_matrix_zoobenthos_nat.xlsx')
    # Data.
    data = dwca_generator.DwcaDataSharkStandard(resources)
    for dataset_filepath in [
                'test_data/SHARK_Zooplankton_2012_SMHI_version_2019-09-26.zip', 
                'test_data/SHARK_Zooplankton_2012_UMSC_version_2019-02-14.zip', 
                'test_data/SHARK_Zooplankton_2013_DEEP_version_2019-02-14.zip', 
                ]:
        data.add_dataset(dataset_filepath)
    data.add_extra_fields()
    data.create_dwca_keys()
    data.map_fields_to_dwc()
    data.cleanup_data()
#     data.translate_species()
#     data.translate_stations()
#     data.translate_fields()
#     data.apply_filter()
    # Format.
    dwca_format = dwca_generator.DwcaFormatStandard(data, resources, )
    dwca_format.create_dwca_parts()
    dwca_format.create_meta_xml()
    dwca_format.create_eml_xml(eml_template = 'templates/epibenthos_nat_eml.xml')
    dwca_format.save_to_archive_file('test_data/TEST.zip', '', '')
    
    # DwC-A Writer.
#     dwca_writer = dwca_generator.DwcaWriter(
#                     datatype='Zoobenthos', 
#                     data=data, 
#                     resources=resources, )
#     dwca_writer.save_dwca(out_file_path='D:/arnold/42_sharkdata_py3/test_data_2/dwca-Zoobenthos-nat-obis.zip', )
    
    
#     # Bacterioplankton.
#     print('\n')
#     print('TEST: Bacterioplankton. ' + str(datetime.datetime.now()))
#     print('')
#     dwca_generator_OLD.DarwinCoreWriter().create_darwincore_archive(
#             datatype='Bacterioplankton', 
#             dataset_dir='D:/arnold/42_sharkdata_py3/test_data/SHARKdata_datasets', 
#             national_data=True,
#             out_file_path='D:/arnold/42_sharkdata_py3/test_data/dwca-bacterioplankton-obis.zip', 
#             )
#         
#     # Epibenthos NAT.
#     print('\n')
#     print('TEST: Epibenthos NAT. ' + str(datetime.datetime.now()))
#     print('')
#     dwca_generator_OLD.DarwinCoreWriter().create_darwincore_archive(
#             datatype='Epibenthos', 
#             dataset_dir='D:/arnold/42_sharkdata_py3/test_data/SHARKdata_datasets', 
#             national_data=True,
#             out_file_path='D:/arnold/42_sharkdata_py3/test_data/dwca-Epibenthos-nat-obis.zip', 
#             )
#         
#     # Epibenthos REG.
#     print('\n')
#     print('TEST: Epibenthos REG. ' + str(datetime.datetime.now()))
#     print('')
#     dwca_generator_OLD.DarwinCoreWriter().create_darwincore_archive(
#             datatype='Epibenthos', 
#             dataset_dir='D:/arnold/42_sharkdata_py3/test_data/SHARKdata_datasets', 
#             national_data=False,
#             out_file_path='D:/arnold/42_sharkdata_py3/test_data/dwca-epibenthos-reg-obis.zip', 
#             )
#        
#        
#        
#        
#        
#         
#     # Zoobenthos NAT.
#     print('\n')
#     print('TEST: Zoobenthos NAT. ' + str(datetime.datetime.now()))
#     print('')
#     dwca_generator_OLD.DarwinCoreWriter().create_darwincore_archive(
#             datatype='Zoobenthos', 
#             dataset_dir='D:/arnold/42_sharkdata_py3/test_data/SHARKdata_datasets', 
#             national_data=True,
#             out_file_path='D:/arnold/42_sharkdata_py3/test_data/dwca-Zoobenthos-nat-obis.zip', 
#             )
#          
#     # Zoobenthos REG.
#     print('\n')
#     print('TEST: Zoobenthos REG. ' + str(datetime.datetime.now()))
#     print('')
#     dwca_generator_OLD.DarwinCoreWriter().create_darwincore_archive(
#             datatype='Zoobenthos', 
#             dataset_dir='D:/arnold/42_sharkdata_py3/test_data/SHARKdata_datasets', 
#             national_data=False,
#             out_file_path='D:/arnold/42_sharkdata_py3/test_data/dwca-Zoobenthos-reg-obis.zip', 
#             )
#        
#       
#       
#     # Greyseal.
#     print('\n')
#     print('TEST: Greyseal. ' + str(datetime.datetime.now()))
#     print('')
#     dwca_generator_OLD.DarwinCoreWriter().create_darwincore_archive(
#             datatype='GreySeal', 
#             dataset_dir='D:/arnold/42_sharkdata_py3/test_data/SHARKdata_datasets', 
#             national_data=False,
#             out_file_path='D:/arnold/42_sharkdata_py3/test_data/dwca-greyseal-obis.zip', 
#             )
#     # Harbourseal.
#     print('\n')
#     print('TEST: Harbourseal. ' + str(datetime.datetime.now()))
#     print('')
#     dwca_generator_OLD.DarwinCoreWriter().create_darwincore_archive(
#             datatype='HarbourSeal', 
#             dataset_dir='D:/arnold/42_sharkdata_py3/test_data/SHARKdata_datasets', 
#             national_data=False,
#             out_file_path='D:/arnold/42_sharkdata_py3/test_data/dwca-harbourseal-obis.zip', 
#             )
#     # Ringedseal.
#     print('\n')
#     print('TEST: Ringedseal. ' + str(datetime.datetime.now()))
#     print('')
#     dwca_generator_OLD.DarwinCoreWriter().create_darwincore_archive(
#             datatype='RingedSeal', 
#             dataset_dir='D:/arnold/42_sharkdata_py3/test_data/SHARKdata_datasets', 
#             national_data=False,
#             out_file_path='D:/arnold/42_sharkdata_py3/test_data/dwca-ringedseal-obis.zip', 
#             )
#        
#     # JERICO.
#     print('\n')
#     print('TEST: JERICO. ' + str(datetime.datetime.now()))
#     print('')
#     dwca_generator_OLD.DarwinCoreWriter().create_darwincore_archive(
#             datatype='Phytoplankton-JERICO', 
#             dataset_dir='D:/arnold/42_sharkdata_py3/test_data/SHARKdata_datasets', 
#             national_data=False,
#             out_file_path='D:/arnold/42_sharkdata_py3/test_data/dwca-phytoplankton-jerico_TEST.zip', 
#             )
#     # JERICO-IFCB.
#     print('\n')
#     print('TEST: JERICO-IFCB. ' + str(datetime.datetime.now()))
#     print('')
#     dwca_generator_OLD.DarwinCoreWriter().create_darwincore_archive(
#             datatype='Phytoplankton-JERICO-IFCB', 
#             dataset_dir='D:/arnold/42_sharkdata_py3/test_data/SHARKdata_datasets', 
#             national_data=False,
#             out_file_path='D:/arnold/42_sharkdata_py3/test_data/dwca-phytoplankton-jerico-ifcb_TEST.zip', 
#             )
#     
#     
#     print('')
#     print('TEST: Finished. ' + str(datetime.datetime.now()))

