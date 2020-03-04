#!/usr/bin/python3
# -*- coding:utf-8 -*-
#
# Copyright (c) 2019-present SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).

import pathlib
import zipfile
import time
import datetime
import pytz

""" """
def singleton(cls):
    """ """
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


def create_extra_key(row_dict, key_list):
    """ """
    key_string = ''
    try:
#            key_list = [str(row_dict.get(item, '')) for item in key_columns if row_dict.get(item, False)]
        value_list = []
        for key in key_list:
            value = str(row_dict.get(key, '')) 
            if value:
                value_list.append(key + ':' + value.replace(',', '.'))
        key_string = ','.join(value_list)
    except:
        key_string = 'ERROR: Failed to generate key-string'
    # Replace swedish characters.
    key_string = key_string.replace('Å', 'A')
    key_string = key_string.replace('Ä', 'A')
    key_string = key_string.replace('Ö', 'O')
    key_string = key_string.replace('å', 'a')
    key_string = key_string.replace('ä', 'a')
    key_string = key_string.replace('ö', 'o')
    key_string = key_string.replace('µ', 'u')
    #
    return key_string


def is_daylight_savings_time(date_str, zone_name='Europe/Stockholm'):
    """ Returns True if DST=Daylight Savings Time. """
    try:
        localtime = pytz.timezone(zone_name)
        datetime_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        localized_date = localtime.localize(datetime_date)
        return bool(localized_date.dst())
    except:
        return False


class ZipArchive():
    """ """
    def __init__(self, zip_file_name):
        """ """
        self._filepathname = pathlib.Path(zip_file_name)
        # Delete old version, if exists.
        if self._filepathname.exists():
            self._filepathname.unlink() # Unlink = remove.
            time.sleep(0.5) # Time needed to remove the file.
  
    def appendZipEntry(self, zip_entry_name, content):
        """ """
        ziparchive = None
        try:
            ziparchive = zipfile.ZipFile(self._filepathname, 'a', zipfile.ZIP_DEFLATED) # Append. 
            ziparchive.writestr(zip_entry_name, content)
        finally:
            if ziparchive:
                ziparchive.close()
 
    def appendFileAsZipEntry(self, zip_entry_name, file_path):
        """ """
        ziparchive = None
        try:
            ziparchive = zipfile.ZipFile(self._filepathname, 'a', zipfile.ZIP_DEFLATED) # Append. 
            ziparchive.write(file_path, zip_entry_name)
        finally:
            if ziparchive:
                ziparchive.close()
