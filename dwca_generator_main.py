#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2020-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import dwca_generator


def generate_dwca(config_file):
    """ """
    print("\n\n\n=== Processing: ", config_file)

    # Config and EML content.
    dwca_gen_config = dwca_generator.DwcaGeneratorConfig(config_file)
    dwca_gen_config.load_config()
    eml_content_rows = dwca_gen_config.generate_eml_content()

    # Prepare data.
    print("\n=== Preparing data ===")
    filters = dwca_generator.DwcaFilters(dwca_gen_config.filters_files)
    translate = dwca_generator.DwcaTranslate(dwca_gen_config.translate_files)
    source_data = dwca_generator.DwcaDataSharkStandard(
        dwca_gen_config, filters, translate
    )
    for dataset_filepath in dwca_gen_config.source_files:
        source_data.add_shark_dataset(dataset_filepath)
    source_data.create_dwca_keys()
    source_data.cleanup_data()

    # Create and save DwC-A.
    print("\n=== Creating DwC-A ===")
    species_info = dwca_generator.DwcaSpeciesWorms(
        taxa_file_path=dwca_gen_config.taxa_worms_file
    )
    dwca_format = dwca_generator.DwcaFormatStandard(
        source_data, dwca_gen_config, species_info, translate
    )
    dwca_format.create_dwca_event()
    dwca_format.create_dwca_occurrence()
    dwca_format.create_dwca_measurementorfact()
    dwca_format.extract_metadata()
    dwca_format.add_metadata_to_eml(eml_content_rows)
    dwca_format.create_meta_xml()
    dwca_format.save_to_archive_file()

    # Print missing taxa.
    missing_taxa_list = species_info.get_missing_taxa_list()
    if len(missing_taxa_list) > 0:
        print("\n   Missing taxa: ")
        for taxa in missing_taxa_list:
            print("   - ", taxa)

    print("\n=== Finished: ", config_file)

# For TEST.
if __name__ == "__main__":
    """ """
    # Test configs.
    config_files = [
        "dwca_config/dwca_bacterioplankton_nat.yaml",
        "dwca_config/dwca_zooplankton_nat.yaml",
        "dwca_config/dwca_zoobenthos_nat.yaml",
        "dwca_config/dwca_phytoplankton_nat.yaml",
    ]
    for config_file in config_files:
        generate_dwca(config_file)
