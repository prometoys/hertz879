#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
import pandas as pd
import numpy as np
import re
import datetime
import csv
import codecs
import os
import sys
import random
import subprocess as sp


# **CSV Reader Unicode und so Python3 kompatibel gestalten**
def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

def build_sched_codes(group_str, filepath_str, sc_dict, usrdef_str):
    result = []
    ud = "" + usrdef_str
    print("Group: "+group_str)
    if group_str in sc_dict:
        sc_list = sc_dict[group_str]
        for sched_code in sc_list:
            if "filepath" in sched_code:
                sched_str = ""
                if "Nacht-Hart" in filepath_str:
                    sched_str = "gRocK"
                elif "Nacht-Weich" in filepath_str:
                    sched_str = "gPoP"
                else:
                    sched_str = "xUncertain"
                    ud = ud + " nachpflege2014"
                sched_code = sched_str
            elif "bettentauglich" in sched_code:
                ud = ud + " bettentauglich"
                sched_code = "sInstrumnt"
            # check for double entries and if sched_code contains something
            if not any(sched_code in s for s in result) and sched_code:
                result.append("--add-scheduler-code=%s" % (sched_code))
    return result, ud

# **Scheduler-Codes-Transfertabelle importieren und als `Dict` aufbereiten**
def gen_transfertable(filename):
    # Erste Variante ist nicht Python3 konform.
    # importfile = csv.reader(open(filename,'rU'), 
    #                        delimiter=';', quotechar='"')
    importfile = unicode_csv_reader(codecs.open(filename,'rU', encoding='utf-8'), delimiter=b';', quotechar=b'"')

    data = list(importfile)
    data = [x for x in data if not (len(x)==0 or x[0].strip().startswith("#"))]
    sched_code_dict = {}
    for x in data:
        array = []
        for y in x[1].split(","):
            array.append(y.strip())
        sched_code_dict[x[0]] = array
        
    return sched_code_dict

transfertabe_filename = "schedcodes2014-transfertable.csv"
transfer_dict = gen_transfertable(transfertabe_filename)

#for item in transfer_dict:
#    print(item)

b,u=build_sched_codes(u"Z-Löwenhertz", "Nacht-Weich\A Forest - The Shepherd.mp3", transfer_dict, "2014import")
print(b)
