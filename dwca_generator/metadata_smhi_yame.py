#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2022-present SMHI, Swedish Meteorological and Hydrological Institute
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import jinja2

# import slugify


class MetadataSmhiYame(object):
    """ """
    def __init__(self, source, template, target):
    # def __init__(self, dwca_gen_config):
        """ """
        # self.dwca_gen_config = dwca_gen_config
        self.content_rows = []
        # self.cleanup_metadata(self.dwca_gen_config.metadata)

        # self.metadata_source = self.dwca_gen_config.metadata_source
        # self.metadata_template = self.dwca_gen_config.metadata_template
        # self.metadata_target = self.dwca_gen_config.metadata_target
        self.metadata_source = source
        self.metadata_template = template
        self.metadata_target = target

    def add_metadata(self, metadata_content_auto):
        """ """
        if len(self.metadata_template) > 0:
            metadata_template_path = pathlib.Path(self.metadata_template)
            loader = jinja2.FileSystemLoader(searchpath=metadata_template_path.parent)
            environment = jinja2.Environment(loader=loader)
            # template_file = "yame_zoobenthos_nat_template_en.json"
            template = environment.get_template(metadata_template_path.name)
            outputText = template.render(
                metadata=self.metadata_source, metadata_auto=metadata_content_auto
            )
            self.content_rows = outputText
        else:
            self.content_rows = ""

        # ### TEST slugify:
        # url_title = self.dwca_gen_config.metadata["titles"]["NAT"]["zoobenthos"]["en"]
        # slug = slugify.slugify(url_title)
        # print("TEST slugify:")
        # print(url_title)
        # print(slug)

    def save_to_file(self):
        """ """
        if len(self.metadata_target) > 0:
            # metadata_file = pathlib.Path("yame_zoobenthos_nat_en.json")
            metadata_file = pathlib.Path(self.metadata_target)
            with metadata_file.open("w", encoding="utf8") as out_file:
                # out_file.write("\n".join(self.content_rows))
                # out_file.write("".join(self.content_rows))
                out_file.write(self.content_rows)

    def cleanup_metadata(self, metadata):
        """ """
        new_metadata = self.stripValues(metadata)
        self.dwca_gen_config.metadata = new_metadata

    def stripValues(self, data):
        if isinstance(data, dict):
            # return {k:self.stripValues(v) for k, v in data.items() if k is not None and v is not None}
            return {k: self.stripValues(v) for k, v in data.items()}
        elif isinstance(data, list):
            # return [self.stripValues(item) for item in data if item is not None]
            return [self.stripValues(item) for item in data]
        elif isinstance(data, tuple):
            # return tuple(self.stripValues(item) for item in data if item is not None)
            return tuple(self.stripValues(item) for item in data)
        elif isinstance(data, set):
            # return {self.stripValues(item) for item in data if item is not None}
            return {self.stripValues(item) for item in data}
        else:
            # return data
            if isinstance(data, str):
                return data.strip()
            else:
                return data
