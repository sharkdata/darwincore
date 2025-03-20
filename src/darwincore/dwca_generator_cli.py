#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2020-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib

import click

from darwincore import dwca_generator_main

global dwca_configs


@click.command()
@click.option(
    "--row",
    default=0,
    prompt="Execute row",
    help="Row number used to select which YAML-file to generate DwC-A from.",
)
def run_dwca_generator_command(row):
    """ """
    global dwca_configs
    if (row < 0) or (row > len(dwca_configs)):
        print("\n\nERROR: Wrong value. Please try again.\n\n")
        return

    generator = dwca_generator_main.DwcaGenerator()
    if row == 0:
        for config_file in dwca_configs:
            generator.generate_dwca(config_file)
    else:
        generator.generate_dwca(dwca_configs[row - 1])


def main():
    global dwca_configs
    dwca_configs = []
    for file_path in pathlib.Path("dwca_config").glob("dwca_*.yaml"):
        dwca_configs.append(str(file_path))
    dwca_configs = sorted(dwca_configs)
    # Print before command.
    print("\n\nDarwinCore-Archive generator.")
    print("-----------------------------")
    print("Select row number. Press enter to run all.")
    print("Press Ctrl-C to terminate.\n")
    for index, row in enumerate(dwca_configs):
        print(index + 1, "  ", row)
    print("")
    # Execute command.
    run_dwca_generator_command()


if __name__ == "__main__":
    main()
