#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2020-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import logging
from pathlib import Path

from darwincore.dwca_generator.dwca_data_shark import DwcaDataSharkStandard
from darwincore.dwca_generator.dwca_filters import DwcaFilters
from darwincore.dwca_generator.dwca_format_standard import DwcaFormatStandard
from darwincore.dwca_generator.dwca_generator_config import DwcaGeneratorConfig
from darwincore.dwca_generator.dwca_taxa_worms import TaxaWorms
from darwincore.dwca_generator.dwca_transform_data import DwcaTransformData
from darwincore.dwca_generator.dwca_translate import DwcaTranslate
from darwincore.dwca_generator.metadata_content_auto import MetadataContentAuto
from darwincore.dwca_generator.metadata_dwca_eml import MetadataDwcaEml
from darwincore.dwca_generator.metadata_smhi_yame import MetadataSmhiYame
from darwincore.dwca_generator.shark_fetch import FetchOptions

logger = logging.getLogger("dwca_generator")


class DwcaGenerator:
    """ """

    def __init__(self):
        """ """

    def generate_dwca(self, config_file: Path, fetch_options: FetchOptions | None = None):
        """ """
        # Config and EML content.
        dwca_gen_config = DwcaGeneratorConfig(config_file, fetch_options)
        dwca_gen_config.load_config()

        # Setup logging.
        log_file_name = dwca_gen_config.dwca_target
        log_file_name = log_file_name.replace(".zip", "_LOG.txt")
        self.setup_logging(log_file_name)

        if not dwca_gen_config.source_files:
            logger.info(f"No source files, skipping: {config_file.name}")
            return

        logger.info("")
        logger.info("")
        logger.info("")
        logger.info(f"=== Processing: {config_file.name}")

        # Prepare EML content.
        eml = False
        if len(dwca_gen_config.eml_definitions.keys()) > 0:
            eml_content_rows = dwca_gen_config.generate_eml_content()
            eml = True
        else:
            logger.info("")
            logger.info("=== no eml definitions ===")

        # Prepare data.
        logger.info("")
        logger.info("=== Preparing data ===")
        filters = DwcaFilters(dwca_gen_config.filters_files)
        translate = DwcaTranslate(dwca_gen_config.translate_files)
        source_data = DwcaDataSharkStandard(dwca_gen_config, filters, translate)
        for dataset_filepath in dwca_gen_config.source_files:
            source_data.add_shark_dataset(dataset_filepath)
        # source_data.create_dwca_keys()
        source_data.cleanup_data()
        source_data.create_dwca_keys()

        transform = DwcaTransformData(dwca_gen_config.transform_files)

        # Create and save DwC-A.
        logger.info("")
        logger.info("=== Creating DwC-A ===")
        species_info = TaxaWorms(taxa_file_path=dwca_gen_config.taxa_worms_file)
        dwca_format = DwcaFormatStandard(
            source_data,
            dwca_gen_config,
            species_info,
            translate,
            transform,
        )
        dwca_format.create_dwca_event()
        dwca_format.create_dwca_occurrence()
        dwca_format.create_dwca_measurementorfact()

        # Metadata.
        metadata_content = MetadataContentAuto()
        dwca_event = dwca_format.dwca_event
        dwca_measurementorfact = dwca_format.dwca_measurementorfact
        metadata_content.extract_metadata(dwca_event, dwca_measurementorfact)

        # Metadata DarwinCore EML.
        logger.info("")
        logger.info("=== Adding metadata for eml files ===")
        metadata_eml = MetadataDwcaEml()
        if eml:
            metadata_eml.add_metadata_to_eml(eml_content_rows, metadata_content)

        # Metadata SMHI YAME.
        # metadata_smhi_yame = dwca_generator.MetadataSmhiYame(dwca_gen_config)
        metadata_smhi_yame = MetadataSmhiYame(
            dwca_gen_config.metadata_source,
            dwca_gen_config.metadata_template,
            dwca_gen_config.metadata_target,
        )
        logger.info("")
        logger.info("=== Adding metadata for SMHI YAME ===")
        if metadata_smhi_yame.metadata_target == "":
            logger.info("yame metadata not created, no target")
        else:
            logger.info(f"yame metadata target {metadata_smhi_yame.metadata_target}")
            logger.info(f"template {metadata_smhi_yame.metadata_template}")
        metadata_smhi_yame.add_metadata(metadata_content)
        metadata_smhi_yame.save_to_file()

        # The meta.xml description file for DwC-A.
        dwca_format.create_meta_xml()

        # Generate zip archive file.
        dwca_format.save_to_archive_file(metadata_eml)

        # Print missing taxa.
        missing_taxa_list = species_info.get_missing_taxa_list()
        if len(missing_taxa_list) > 0:
            logger.info("")
            logger.info("Missing taxa: ")
            for taxa in missing_taxa_list:
                logger.warning("   - " + taxa)

        logger.info("")
        logger.info(f"=== Finished: {config_file.name}")

        # Logger test:
        # logger.debug("debug")
        # logger.info("info")
        # logger.warning("warning")
        # logger.error("error")
        # logger.critical("critical")

    def setup_logging(self, log_file_name):
        """Log to a new file, replacing the log file of any previous config."""
        logger.setLevel(logging.DEBUG)
        for handler in list(logger.handlers):
            if isinstance(handler, logging.FileHandler):
                logger.removeHandler(handler)
                handler.close()
        # Mode "w" overwrites any old log file with the same name.
        file_handler = logging.FileHandler(log_file_name, mode="w")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s : %(message)s")
        )
        logger.addHandler(file_handler)


# Add filter to console to avoid huge error lists.
class ConsoleFilter(logging.Filter):
    def filter(self, record):
        return record.levelno in [logging.INFO, logging.WARNING]
        # return record.levelno in [logging.DEBUG, logging.INFO, logging.WARNING]


def setup_console_logging():
    """Set up console logging. Call once at program start."""
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    console_handler.addFilter(ConsoleFilter())
    logger.addHandler(console_handler)


def main():
    setup_console_logging()
    # Test configs.
    config_files = [
        "dwca_config/dwca_bacterioplankton_nat.yaml",
        "dwca_config/dwca_zooplankton_nat.yaml",
        "dwca_config/dwca_zoobenthos_nat.yaml",
        "dwca_config/dwca_phytoplankton_nat.yaml",
        "dwca_config/dwca_phytoplankton_ifcb.yaml",
        # "dwca_config/dwca_phytoplankton_reg_recip_proj.yaml",
        # "dwca_config/dwca_zoobenthos_reg_recip_proj.yaml",
        "dwca_config/dwca_harbourseal_nat.yaml",
        "dwca_config/dwca_greyseal_nat.yaml",
        "dwca_config/dwca_ringedseal_nat.yaml",
        "dwca_config/dwca_phytoplankton_slv_biotox.yaml",
        "dwca_config/dwca_seal_pathology.yaml",
        "dwca_config/dwca_picoplankton_nat_reg.yaml",
        "dwca_config/dwca_epibenthos_nat.yaml",
        "dwca_config/dwca_epibenthos_reg_recip_proj.yaml",
        "dwca_config/dwca_harbour_porpoise_nat.yaml",
    ]
    generator = DwcaGenerator()
    for config_file in config_files:
        generator.generate_dwca(Path(config_file))

    print("=== Finished. ===")


if __name__ == "__main__":
    main()
