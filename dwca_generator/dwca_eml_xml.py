#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib

class DarwinCoreEmlXml():
    """ """
    def __init__(self, resources, target_dwca_path='DwC-A_TEST.zip'):
        """
        EML = Ecological Metadata Language.
        """
        self.target_dwca_path = pathlib.Path(target_dwca_path)
        # Reference to DwcaResources object. 
        self.resources = resources
    
    def create_eml_xml(self, eml_path):
        """ """
        eml = []
        eml_replace_dict = {}
        
        for row_dict in self.resources.eml_metadata:
            dwc_export_filename = row_dict.get('dwc_export_filename', '')
            eml_replace_keyword = row_dict.get('eml_replace_keyword', '')
            text = row_dict.get('text', '')
            
            
            
            export_filename = self.target_dwca_path.name
            
            if (dwc_export_filename == '') or (dwc_export_filename == export_filename):
                
                
                
                
                
                if eml_replace_keyword and text:
                    if eml_replace_keyword == 'REPLACE-coverage-taxonomicCoverage':
                        text = self.generateTaxonomicCoverage(text)
                    eml_replace_dict[eml_replace_keyword] = text
        
        with pathlib.Path(eml_path).open('r', encoding='cp1252') as eml_file:
            for line in eml_file:
                
                if 'REPLACE' in line:
                    for replace_keyword, replace_text in eml_replace_dict.items():
                        if replace_keyword in line:
                            line = line.replace(replace_keyword, replace_text)
                
                eml.append(line.rstrip())
        
        return eml


    def generateTaxonomicCoverage(self, in_text):
        """ """
        out_text = ''
        if in_text:
            out_text += '<generalTaxonomicCoverage>\n'
            out_text += '\t\t\tThe dataset contains species within the following taxa: \n'
            out_text += '\t\t</generalTaxonomicCoverage>\n'
            
            for text_pair in in_text.split(','):
                text_rank_taxa = text_pair.split(':')
                if len(text_rank_taxa) >=2 and text_rank_taxa[0] and text_rank_taxa[1]:
                    out_text += '\t\t\t<taxonomicClassification>\n'
                    out_text += '\t\t\t\t<taxonRankName>' + text_rank_taxa[0] + '</taxonRankName>\n'
                    out_text += '\t\t\t\t<taxonRankValue>' + text_rank_taxa[1] + '</taxonRankValue>\n'
                    out_text += '\t\t\t</taxonomicClassification>\n'
        
        return out_text