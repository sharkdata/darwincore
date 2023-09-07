#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2020-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import requests
import json
import pathlib

def post_to_yame_prod(filepath):

    with open(filepath, encoding='utf-8') as f:
        metadata_file = json.load(f)

    yame_id = metadata_file["metadata"]["fileIdentifier"]

    headers = {
        'Content-Type': 'application/json',
    }
    print(f"updating {filepath} with yame ID {yame_id} in yame prod")
    response = requests.put(f"https://sid-metadata.smhi.se/yamr/apipri/{yame_id}", headers=headers, json=metadata_file)
    print(response.text)

if __name__ == "__main__":
    """kör detta för att posta yame json metadatafiler till en befintlig metadatapost i yamr"""

    # TODO: make this similar to dwca_generator_cli to let the user choose files to upload from a list.

    # OBS för att köra alla yame json filer i mappen data_out skriv
    # .glob("yame_*.json")
    # fär att köra endast en vald skriv t.ex.
    # .glob("yame_pico*nat*.json")
    for file_path in pathlib.Path("data_out").glob("yame_physical*.json"):
        print(file_path)
        post_to_yame_prod(file_path)
