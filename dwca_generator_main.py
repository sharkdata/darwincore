#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2020-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

# import pathlib
# import yaml
# import dict2xml
# import collections.abc

import dwca_generator

if __name__ == "__main__":
    """ """

    config_files = [
        "dwca_config/dwca_bacterioplankton_nat.yaml",
    ]

    for config_file in config_files:
        dwca_gen_config = dwca_generator.DwcaGeneratorConfig(config_file)
        dwca_gen_config.load_config()
        eml_content = dwca_gen_config.generate_eml_content()
        # print(eml_content)

        source_data = dwca_generator.DwcaDataSharkStandard(dwca_gen_config)
        for dataset_filepath in dwca_gen_config.source_files:
            source_data.add_shark_dataset(dataset_filepath)
        source_data.create_dwca_keys()
        # source_data.create_dynamic_fields()
        source_data.cleanup_data()

        species_info = None  # TODO:

        dwca_format = dwca_generator.DwcaFormatStandard(
            source_data, dwca_gen_config, species_info
        )
        dwca_format.create_dwca_parts()
        # dwca_format.extract_metadata()
        dwca_format.create_eml_xml(eml_content)
        dwca_format.create_meta_xml()
        dwca_format.save_to_archive_file()

        # # TEST
        # eml_xml_path = pathlib.Path(dwca_gen.dwca_target)
        # # Write EML.XLM
        # with eml_xml_path.open("w", encoding="utf8") as out_file:
        #     out_file.write(eml_content)
