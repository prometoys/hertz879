#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
#from __future__ import unicode_literals
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

pd.set_option('display.max_columns', 60)
pd.set_option('display.max_rows', 1000)



# ## Hilfsfunktionen

# **Zeit-String in Milisekunden umwandeln.**
def time_convert(timestring):
    timestring = str(timestring)
    ms=0
    factor=3600000
    for i in timestring.split(":"):
        ms= ms+(int(i)*factor)
        factor=factor/60
    return ms


# **Einen String mit Anführungszeichen versehen**
def quote_string(string):
    return '"'+string+'"'

# **Artikel am Ende eines Titels nach vorne schieben.** 
def word_move(artist):
    artist = artist.strip()
    result = artist
    #r = re.compile("(^.*)(, ?)(der|die|das|the)$",re.IGNORECASE)
    r = re.compile("^(.+\s*)+(,\s*)(\w+)$")
    r2 = re.compile("(.*,.*&.*|.*,\s*\S+\s+.*)")
    if "," in artist:
        if not r2.match(artist,0):
            result = r.sub(r"\3 \1",artist).strip()
    return result


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


# Dieser Aufruf ist nicht kompatibel mit Python 3, da die Funktion nicht mit Unicode-Strings zurecht kommt.
# **Für die DRS-Gruppe die jeweiligen Scheduler Codes ausgeben und für `rdimport` aufbereiten** 

def build_sched_codes(group_str, filepath_str, sc_dict, usrdef_str):
    result = []
    ud = "" + usrdef_str
    for sched_code in sc_dict[group_str]:
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


# ## Arbeiten mit der DRS2006 Datenbank
# 
# Zunächst muss die DRS2006-CSV mit OpenOffice aufbereitetet werden (http://wiki.radiohertz.de/rivendell:drs_zu_rivendell-skript). Diese CSV-Datei lesen wir nun ein und speichern es im Objekt *db*.

# read the csv file and generate the db
# filename: importfile
# sep:      CSV seperator
# qc:       quote-char
# enc:      encoding (probably cp850)
# s_rows:   rows to skip (probably 0)
def build_db(filename, sep, qc, enc, s_rows):
    colnames = ['artist','title','length','group','filepath','album','year','comment','end_type','intro','cue_in','fade_in','cue_out','fade_out','information']

    db = pd.read_csv(filename, sep=sep, quotechar=qc, names=colnames, encoding=enc, skiprows=s_rows)

    # **Zeilen mit `NaN`-Werten in wichtigen Spalten werden gelöscht**
    db = db.dropna(subset=["artist","title","length","group","intro","cue_in","fade_in","cue_out","fade_out"])

    # **In allen anderen Spalten werden `NaN`-Werte durch einen leeren String ersetzt**
    db = db.fillna(value="")
    
    # Check, if database has a bad format. If the last column "information"
    # doesn't has the string "Added to Database", then something is wrong.
    errorcheck=db[~db['information'].str.contains("Added to Database")]
    
    if not errorcheck.empty:
        print("[ERROR]: malicious import database")
        print(errorcheck)
        sys.exit(1)

    # ## Konvertieren von Werten
    # 
    # **Wandle den Zeit-String von Intro in ms um.**
    a_time_str_columns = ['length','cue_in','cue_out','intro']
    a_ms_columns = []
    for string in a_time_str_columns:
        new_col = string+'_ms'
        db[new_col] = db[string].apply(time_convert)
        a_ms_columns.append(new_col)

    # Setze die für den Rivendell-Import bestimmte `intro_ms`-Variable auf 0,
    # wenn das Intro genauso lang ist wie der gesamte Song.
    db.loc[db['intro']>=db['length'],'intro_ms'] = 0

    # ### Fade-Zeiten in Millisekunden umwandeln
    db['fade_in'] = db['fade_in'] * 1000
    db['fade_out'] = db['fade_out'] * 1000
    
    return db







def run_rdimport(my_db, my_dict, import_dir, simulate):
    
    path_prefix = import_dir
    cmd_name = ["rdimport"]
    
    if simulate:
        cmd_name = ["echo","rdimport"]
    

    # Create for each row in the database an rdimport 
    for index, row in my_db.iterrows():
        
        # convert Windows URI to UNIX-style
        filepath_str = path_prefix + row['filepath'].replace("\\","/")
        
        if (os.path.exists(filepath_str) or simulate):
            try:
                # preparing metadata
                
                group_str = row['group'].strip()
                title_str = row['title'].strip()
                
                year_str = str(row['year']).strip()
                if re.compile("\d{4}").match(year_str,0):
                    year_str = "--set-string-year=" + year_str
                
                # Do we want move the words after comma to the beginning?
                if True:
                    artist_str = word_move(row['artist'])
                else:
                    artist_str = row['artist']
                artist_str
                
                user_defined_str = "2014tropmiotua"
                
                sched_code, user_defined_str = build_sched_codes(group_str, filepath_str, my_dict, user_defined_str)
                
                talktime_arg = []
                if(row['intro_ms']>0):
                    talktime_arg = ["--set-marker-end-talk=" + str(row['intro_ms'])]
                    talktime_arg.append("--set-marker-start-talk=0")
                    
                # preparing rdimport string
                rdimport_args = [] + cmd_name
                rdimport_args.append("--verbose",)
                rdimport_args.append("--fix-broken-formats")
                rdimport_args.append("--log-mode")
                rdimport_args.append("--set-user-defined="+ user_defined_str)
                rdimport_args.append("--set-string-artist="+ artist_str)
                rdimport_args.append("--set-string-title="+ title_str)
                rdimport_args.append("--set-string-description="+ title_str)
                rdimport_args.append("--set-string-album="+ group_str)
                rdimport_args = rdimport_args + sched_code
                rdimport_args = rdimport_args + talktime_arg
                rdimport_args.append("--set-marker-fadeup=" + str(row['fade_in']))
                rdimport_args.append("--set-marker-fadedown=" + str(row['cue_out_ms']))
                rdimport_args.append("--segue-length="+str(row['fade_out']).strip())
                if year_str:
                    rdimport_args.append(year_str) 
                rdimport_args.append("--normalization-level=-13")
                rdimport_args.append("--autotrim-level=-30")
                rdimport_args.append("--segue-level=-12")
                rdimport_args.append("MUSIK")
                rdimport_args.append(filepath_str)
                
                print("[INFO]: "+ " ".join(rdimport_args)+"\n")
                sys.stdout.flush()
                #sp.call(rdimport_args)
                p = sp.Popen(rdimport_args, bufsize=1)
                p.communicate()
                #(output, err) = p.communicate()
                #p_status = p.wait()
                
                #print("Command output : ",output)
                #print("Command exit status/return code : ", p_status)
 
            except KeyError:
                print("[ERROR]: Group not found: " + quote_string(group_str))
        # This else is, when the file isn't found
            except Exception:
                print(sys.exc_info())
                sys.exit(1)
        else:
            print("[ERROR]: File not found: "+ filepath_str+"\n")
        

def main(argv):
    
    transfertabe_filename = "schedcodes2014-transfertable.csv"
    drs_import_file = 'HRDat-2014-12.TXT'
    audio_import_dir = "/home/admin/ralfdata/Musik/"
    
    # create the "DRS Group to Rivendel Scheduler-Codes" conversion dict.
    transfer_dict = gen_transfertable(transfertabe_filename)
    
    # read the database
    # read_db(filename, sep, qc, enc, s_rows)
    drs_db =build_db(drs_import_file, ",", '"', "cp850", 0)
    
    
    if "--random" in argv:
        numbers=int(argv[2])
        #drs_db = drs_db[drs_db['title'].str.contains('Honig')].head(5)
        #drs_db = drs_db[drs_db['length_ms']>10000].head(5)
        #drs_db = drs_db[~drs_db['year'].str.contains('\d')].head(1)
        #drs_db = drs_db[drs_db['group'] == 'Nacht Hart']
        
        #print(len(drs_db.index))
        #print(drs_db.head(3))
        
        #drs_db = drs_db.iloc[1:2]
        
        db_len = len(drs_db.index)
        
        minimum = min(db_len,numbers)
        random_list = random.sample(xrange(db_len), minimum)
        
        # Print the selected index-numbers 
        #print("Range:" +str(random_list))
        
        drs_db = drs_db.iloc[random_list]
        
        #print(drs_db.head())
        
        #drs_db = drs_db.head(numbers)
    
    
    if "--run" in argv:
        run_rdimport(drs_db, transfer_dict, audio_import_dir, False)
    elif "-s" in argv or "--simulate" in argv:
        run_rdimport(drs_db, transfer_dict, audio_import_dir, True)
    else:
        print("Neither -s or --run, doing nothing.")
    
if __name__ == "__main__":
    main(sys.argv)
    

#### Old Database import syntax
## New database file converted by LibreOffice Calc
#db = pd.read_csv('DatenPerfekt2014-12.csv', sep=";", dtype={'key':unicode}, names=colnames)

## Original testfile. Convertet with Calc (mit skiprows, da hier noch ein Header eingetragen ist)
#db = pd.read_csv('DatenPerfektPandaHeader.csv', sep=";", dtype={'key':unicode}, names=colnames, skiprows=1)

## Original export-file from DRS2006, fixed one row where album contained " (doublequote-char)
#db = pd.read_csv('HRDat-2014-12.TXT', sep=",", quotechar='"', names=colnames, encoding='cp850')

## Original, untouched export-file from DRS2006
#db = pd.read_csv('HRDat.Orig.TXT', sep=",", quotechar='"', names=colnames, encoding='cp850')

