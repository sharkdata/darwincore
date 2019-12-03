#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib

class DarwinCoreEmlXml():
    """ """
    def __init__(self):
        """
        EML = Ecological Metadata Language.
         
        There are no Python libraries for this, but one for R.
        https://github.com/ropensci/EML
        
        This is an early 
        
        Basic structure:
        eml
            - dataset
                - creator
                - title
                - publisher
                - pubDate
                - keywords
                - abstract 
                - intellectualRights
                - contact
                - methods
                - coverage
                    - geographicCoverage
                    - temporalCoverage
                    - taxonomicCoverage
                - dataTable
                    - entityName
                    - entityDescription
                    - physical
                    - attributeList
        """

    def set_package_id(self, 
                       packageId = None, # "f0cda3bf-2619-425e-b8be-8deb6bc6094d",  # from uuid::UUIDgenerate(),
                       system = None): # "uuid", # type of identifier
        """ """
        
    def set_coverage(self, 
                    begin = None, #'2012-06-01', 
                    end = None, # '2013-12-31',
                    sci_names = None, # "Sarracenia purpurea",
                    geographicDescription = None, # geographicDescription,
                    west = None, # -122.44, 
                    east = None, # -117.15, 
                    north = None, # 37.38, 
                    south = None, # 30.00,
                    altitudeMin = None, # 160, 
                    altitudeMaximum = None, # 330,
                    altitudeUnits = None, # "meter"
                    ):
        """ """

    def create_eml_xml(self, eml_path):
        """ """
        eml = []

        with pathlib.Path(eml_path).open('r') as eml_file:
            for line in eml_file:
                eml.append(line.rstrip())

        return eml
