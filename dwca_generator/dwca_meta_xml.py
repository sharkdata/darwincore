#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2013-2016 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

class DarwinCoreMetaXml():
    """ """
    def __init__(self):
        """ """
        #
        self.worms_info_object = None
        
    def create_meta_xml(self, event_columns, ocurrence_columns, measurementorfact_columns):
        """ """
        xml = []
        # XML start.
        xml.append('<archive xmlns="http://rs.tdwg.org/dwc/text/" metadata="eml.xml">')
        
        # Core = Event.
        xml.append('  <core encoding="UTF-8" fieldsTerminatedBy="\\t" linesTerminatedBy="\\r\\n" fieldsEnclosedBy="" ignoreHeaderLines="1" rowType="http://rs.tdwg.org/dwc/terms/Event">')
        xml.append('    <files>')
        xml.append('      <location>event.txt</location>')
        xml.append('    </files>')
        xml.append('    <id index="0" />')
#         xml.append('    <field term="http://rs.tdwg.org/dwc/terms/eventId"/>')
        # Loop over event header.
        index = 0
        for dwc_term in event_columns: 
            if index > 0: # Avoid coreid=eventId.
                xml.append('    <field index="' + str(index) + '" term="' + self.get_dwc_term_url(dwc_term) + '"/>') # Loop.
            index += 1
        #
        xml.append('  </core>')
        
        # Extension = Occurrence.
        xml.append('  <extension encoding="UTF-8" fieldsTerminatedBy="\\t" linesTerminatedBy="\\r\\n" fieldsEnclosedBy="" ignoreHeaderLines="1" rowType="http://rs.tdwg.org/dwc/terms/Occurrence">')
        xml.append('    <files>')
        xml.append('      <location>occurrence.txt</location>')
        xml.append('    </files>')
        xml.append('    <coreid index="0" />')
#         xml.append('    <field term="http://rs.tdwg.org/dwc/terms/eventId"/>')
        # Loop over event header.
        index = 0
        for dwc_term in ocurrence_columns:
            if index > 0: # Avoid coreid=eventId.
                xml.append('    <field index="' + str(index) + '" term="' + self.get_dwc_term_url(dwc_term) + '"/>') # Loop.
            index += 1
        #
        xml.append('  </extension>')
        
        # Extension = ExtendedMeasurementOrFact.
        xml.append('  <extension encoding="UTF-8" fieldsTerminatedBy="\\t" linesTerminatedBy="\\r\\n" fieldsEnclosedBy="" ignoreHeaderLines="1" rowType="http://rs.iobis.org/obis/terms/ExtendedMeasurementOrFact">')
        xml.append('    <files>')
        xml.append('      <location>extendedmeasurementorfact.txt</location>')
        xml.append('    </files>')
        xml.append('    <coreid index="0" />')
#             xml.append('    <field term="http://rs.tdwg.org/dwc/terms/eventId"/>')
        # Loop over event header.
        index = 0
        for dwc_term in measurementorfact_columns:
            if index > 0: # Avoid coreid=eventId.
                xml.append('    <field index="' + str(index) + '" term="' + self.get_dwc_term_url(dwc_term) + '"/>') # Loop.
            index += 1
        #
        xml.append('  </extension>')
        
        # XML end.
        xml.append('</archive>')
        
        return xml
    
    def get_dwc_term_url(self, term):
        """ Used locally. """
        if term == 'license': 
            return 'http://purl.org/dc/terms/license'
        if term == 'rightsHolder': 
            return 'http://purl.org/dc/terms/rightsHolder'
        if term == 'bibliographicCitation': 
            return 'http://purl.org/dc/terms/bibliographicCitation'
        if term == 'accessRights': 
            return 'http://purl.org/dc/terms/accessRights'
        if term == 'references': 
            return 'http://purl.org/dc/terms/references'
        if term == 'type': 
            return 'http://purl.org/dc/terms/type'
        else:
            return 'http://rs.tdwg.org/dwc/terms/' + term
    
