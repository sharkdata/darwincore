#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2020-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import requests
import json
from pathlib import Path

DATA_OUT = Path(__file__).parent / 'data_out'

def put_to_yamr_prod(filepath):

    with open(filepath, encoding='utf-8') as f:
        metadata_file = json.load(f)

    yame_id = metadata_file["metadata"]["fileIdentifier"]

    headers = {
        'Content-Type': 'application/json',
    }
    print(f"updating {filepath} with yame ID {yame_id} in yame prod")
    response = requests.put(f"https://sid-metadata.smhi.se/yamr/apipri/{yame_id}", headers=headers, json=metadata_file)
    print(response.text)

def compare_yamr_to_local(local_file_path):

    with open(local_file_path, encoding='utf-8') as f:
        metadata_file = json.load(f)

    yame_id = metadata_file["metadata"]["fileIdentifier"]

    headers = {
        'Content-Type': 'application/json',
    }

    print(f"get yame ID {yame_id} from yamr prod")
    response = requests.get(url=f"https://sid-metadata.smhi.se/yamr/apipri/{yame_id}", headers=headers)

    # Hämta JSON-data från svaret
    yamr_metadata = response.json()

    compare_json(metadata_file, yamr_metadata["item"]["data"])

    # Spara data till en JSON-fil
    with open(DATA_OUT / f'respone_{yame_id}.json', 'w', encoding="utf-8") as json_file:
        json.dump(yamr_metadata["item"]["data"], json_file, ensure_ascii=False, indent=4)


def compare_json(json1, json2, path=""):
    if isinstance(json1, dict) and isinstance(json2, dict):
        for key in json1.keys() | json2.keys():
            new_path = f"{path}.{key}" if path else key
            if key in json1 and key in json2:
                compare_json(json1[key], json2[key], new_path)
            elif key in json1:
                print(f"Key {new_path} is missing in the second JSON")
            else:
                print(f"Key {new_path} is missing in the first JSON")
    elif isinstance(json1, list) and isinstance(json2, list):
        for index, (item1, item2) in enumerate(zip(json1, json2)):
            compare_json(item1, item2, f"{path}[{index}]")
        if len(json1) > len(json2):
            for index in range(len(json2), len(json1)):
                print(f"Item {path}[{index}] is missing in the second JSON")
        elif len(json2) > len(json1):
            for index in range(len(json1), len(json2)):
                print(f"Item {path}[{index}] is missing in the first JSON")
    else:
        if json1 != json2:
            print(f"Difference at {path}: {json1} != {json2}")

if __name__ == "__main__":
    """kör detta för att posta yame json metadatafiler till en befintlig metadatapost i yamr"""

    # TODO: make this similar to dwca_generator_cli to let the user choose files to upload from a list.

    # OBS för att köra alla yame json filer i mappen data_out skriv
    # .glob("yame_*.json")
    # fär att köra endast en vald skriv t.ex.
    # .glob("yame_pico*nat*.json")
    for file_path in DATA_OUT.glob("yame_greyseal*.json"):
        print(file_path)
        compare_yamr_to_local(file_path)
        put_to_yamr_prod(file_path)
        
