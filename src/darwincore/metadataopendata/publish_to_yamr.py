#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2020-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import json

import requests

from darwincore import DWCA_CONFIG_PATH


def post_to_yamr_prod(yame_id_list):
    if len(yame_id_list) == 0:
        print("no yame IDs provided")
        return

    headers = {
        "Content-Type": "application/json",
    }

    print(f"post yame ID {yame_id_list} to test")
    response = requests.post(
        url="https://sid-metadata.smhi.se/yamr/apipri/publish",
        json={"uuids": yame_id_list},
        headers=headers,
    )
    print(response.text)


def main():
    """kör detta för att posta från yame test till yamr prod"""

    # TODO: make this similar to dwca_generator_cli to let the user choose files to upload
    #  from a list.

    #  - När man är nöjd med resultatet (som man sett i Geonetwork test eller på
    #  www-tst.smhi.se) kan man skicka till prod med:
    #  curl -X POST -H "Content-Type: application/json" -d '{"uuids":
    #  ["9d401958-4726-4a0c-b248-5218995f5e9d"]}'
    #  "https://sid-metadata.smhi.se/yamr/apipri/merge/prod"

    # - Innan man ser detta i geonetwork prod eller på www.smhi.se så måste ovanstående
    # jobb ha körts igen.

    datatype_map_path = DWCA_CONFIG_PATH / "metadata_templates/fileID_datatype_match.json"
    with datatype_map_path.open(encoding="utf-8") as f:
        fileID_datatype_match = json.load(f)

    get_datatype_for_id = {id: datatype for datatype, id in fileID_datatype_match.items()}

    yame_id_list = [
        fileID_datatype_match[datatype] for datatype in ["planktonimaging_ifcb"]
    ]

    # phytoplankton_reg_recip_proj
    # phytoplankton_nat
    # adcp_nat

    for id in yame_id_list:
        print(f"post {get_datatype_for_id.get(id, 'unkown datatype with id:')} {id}")

    post_to_yamr_prod(yame_id_list)

    # publicera metadatapost. det här är steg 2 av 2 för att posta till öppna data
    # skördningen verkar ske någon minut över heltimma - HH:03 kanske


if __name__ == "__main__":
    main()
