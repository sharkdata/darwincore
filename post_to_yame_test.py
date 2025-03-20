#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2020-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import json

import requests


def post_to_yame_prod(yame_id_list):
    headers = {
        "Content-Type": "application/json",
    }

    print(f"post yame ID {yame_id_list} to test")
    response = requests.post(
        url="https://sid-metadata.smhi.se/yamr/apipri/merge/test",
        json={"uuids": yame_id_list},
        headers=headers,
    )
    print(response.text)


if __name__ == "__main__":
    """
    Kör detta för att skicka en metadata post i yamr till test:
    curl -X POST -H "Content-Type: application/json" -d
    '{"uuids": ["9d401958-4726-4a0c-b248-5218995f5e9d"]}'
    "https://sid-metadata.smhi.se/yamr/apipri/merge/test"

     hh:55 körs ett jobb i ecFlow som synkar de ändringar man gjort via API'et (eller i
     Yame) till respektive miljö. Resultatet av denna synkning syns i Yame.

    Alltså, om ni har ändrat en post och skickat denna till test enligt stegen ovan så
    syns den ändringen på https://sid-metadata-tst.smhi.se/yame/ (med ett ifyllt hänglås
    eftersom posten inte är skickad till produktion).
    """

    # TODO: make this similar to dwca_generator_cli to let the user choose files to upload
    #  from a list.
    with open(
        "dwca_config/metadata_templates/fileID_datatype_match.json", encoding="utf-8"
    ) as f:
        fileID_datatype_match = json.load(f)

    get_datatype_for_id = {id: datatype for datatype, id in fileID_datatype_match.items()}

    yame_id_list = [
        "ce89ba58-f397-47a4-8493-8b5c711fd1ab",
        "e19d5237-286c-499e-94aa-b3d9c5d27c5e",
        "e4857210-2dd8-11ed-84f0-5b3e6bab28c1",
        "2124a8b6-2f07-415c-ba55-fb16afc5f1fc",
        "c4a67335-ad22-4d79-9175-62d54d55409f",
    ]

    # for id in yame_id_list:
    id = "ce89ba58-f397-47a4-8493-8b5c711fd1ab"
    print(f"post {get_datatype_for_id.get(id, 'unkown datatype with id:')} {id}")
    post_to_yame_prod([id])

    # den här koden är inaktuell efter 2024-04-22
