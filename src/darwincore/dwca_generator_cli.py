#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2020-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
from datetime import date, datetime

import click

from darwincore import dwca_generator_main
from darwincore.dwca_generator.shark_fetch import FetchOptions
from darwincore.errors import DarwinCoreError

row_option = click.option(
    "--row",
    "-r",
    type=int,
    help="Row number of the YAML-file to generate DwC-A from. 0 selects all.",
)
date_type = click.DateTime(formats=["%Y-%m-%d"])


@click.group(invoke_without_command=True)
@row_option
@click.pass_context
def cli(ctx: click.Context, row: int | None):
    """Generate DwC-A from local SHARK datasets."""
    if ctx.invoked_subcommand is not None:
        return
    fetch_options = None
    if row is None:
        row = prompt_for_row(find_dwca_configs())
        if click.confirm("Fetch data from SHARK?", default=False):
            fetch_options = FetchOptions()
    run_dwca_generator(row, fetch_options)


@cli.command()
@row_option
@click.option(
    "--from",
    "from_date",
    type=date_type,
    help="Earliest publication date of the dataset version (not sampling date).",
)
@click.option(
    "--to",
    "to_date",
    type=date_type,
    help="Latest publication date of the dataset version (not sampling date).",
)
def fetch(row: int | None, from_date: datetime | None, to_date: datetime | None):
    """Generate DwC-A from datasets downloaded from SHARK."""
    fetch_options = create_fetch_options(
        from_date=from_date.date() if from_date else None,
        to_date=to_date.date() if to_date else None,
    )
    run_dwca_generator(row, fetch_options)


def create_fetch_options(from_date: date | None, to_date: date | None) -> FetchOptions:
    try:
        return FetchOptions(from_date=from_date, to_date=to_date)
    except DarwinCoreError as e:
        raise click.BadParameter(str(e))


def find_dwca_configs() -> list[pathlib.Path]:
    return sorted(pathlib.Path("dwca_config").glob("dwca_*.yaml"))


def prompt_for_row(dwca_configs: list[pathlib.Path]) -> int:
    print("\n\nDarwinCore-Archive generator.")
    print("-----------------------------")
    print("Select configuration by number.")
    print("Press Ctrl-C to terminate.\n")
    print(" 0.  ALL CONFIGURATIONS")
    for index, config_file in enumerate(dwca_configs, start=1):
        print(f"{index:>2}.  {config_file.name}")
    print("")
    return click.prompt(
        f"Execute configuration (0 - {len(dwca_configs)}):",
        type=click.IntRange(0, len(dwca_configs)),
        default=0,
    )


def run_dwca_generator(row: int | None, fetch_options: FetchOptions | None):
    dwca_configs = find_dwca_configs()
    if row is None:
        row = prompt_for_row(dwca_configs)

    if (row < 0) or (row > len(dwca_configs)):
        print("\n\nERROR: Wrong value. Please try again.\n\n")
        return

    selected_configs = dwca_configs if row == 0 else [dwca_configs[row - 1]]
    click.echo("Selected configurations:")
    for config_file in selected_configs:
        click.echo(f"   {config_file.name}")

    generator = dwca_generator_main.DwcaGenerator()
    failed_configs = []
    for config_file in selected_configs:
        try:
            generator.generate_dwca(config_file, fetch_options)
        except DarwinCoreError as e:
            click.echo(f"ERROR: {config_file}: {e}", err=True)
            failed_configs.append(config_file)

    if failed_configs:
        click.echo(f"{len(failed_configs)} config files failed:", err=True)
        for config_file in failed_configs:
            click.echo(f"   {config_file.name}", err=True)
        raise SystemExit(1)


def main():
    dwca_generator_main.setup_console_logging()
    cli()


if __name__ == "__main__":
    main()
