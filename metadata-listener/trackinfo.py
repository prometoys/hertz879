#!/usr/bin/python
# -*- coding: utf8 -*-
import socket, re, sys
from optparse import OptionParser


# Trackinfo liest nur Textdateien aus:
#
# tmp/xspf oder tmp/plain
#
# stream/vorbis sind deprecated

# TODO: Read path from config file (.hirse.rc)
TMP_DIR="tmp/"
XSPF_FRAGMENT_FILENAME=TMP_DIR+'xspf-current-fragment'
PLAIN_FRAGMENT_FILENAME=TMP_DIR+'plain-current-fragment'
CURRENT_ARTIST_FILENAME=TMP_DIR+'current.artist'
CURRENT_TITLE_FILENAME=TMP_DIR+'current.title'

DEBUG=False

# Debug-Funktion
def error_print(string):
    print >> sys.stderr, string

# Todo: arbeitet nicht mit option.verbose / optparse zusammen, warum?!
def debug(string):
    if DEBUG:
        error_print(string)

# Methoden, die vom OptionParser aufgerufen werden sollen
# auslagern in neues trackinfo?
def print_vorbis(option, opt, value, parser):
    debug("vorbis: deprecated")
    plain_file = open(PLAIN_FRAGMENT_FILENAME,'r')
    output = ""
    for line in plain_file:
        if "artist" in line:
            output = output + line
        if "title" in line:
            output = output + "title=" + line
# without .rstrip('\n') to be conform with old trackinfo output
    print output

def print_plain(option, opt, value, parser):
    plain_file = open(PLAIN_FRAGMENT_FILENAME,'r')
    output = ""
    for line in plain_file:
        output = output + line
    print output.rstrip('\n')

def print_stream(option, opt, value, parser):
    debug("stream: deprecated")
    plain_file = open(PLAIN_FRAGMENT_FILENAME,'r')
    output = ""
    for line in plain_file:
        if "artist" in line:
            artist = re.sub(r'^artist=', 'artist=[Hertz 87,9] ', line)
            output = output + artist
        if "title" in line:
            output = output + "title=" + line
    print output.rstrip('\n')

def print_current_artist(option, opt, value, parser):
    plain_file = open(CURRENT_ARTIST_FILENAME,'r')
    output = ""
    for line in plain_file:
        output = output + line
    print output.rstrip('\n')
    
def print_current_title(option, opt, value, parser):
    plain_file = open(CURRENT_TITLE_FILENAME,'r')
    output = ""
    for line in plain_file:
        output = output + line
    print output.rstrip('\n')
    
def print_xspf(option, opt, value, parser):
    xspf_file = open(XSPF_FRAGMENT_FILENAME,'r')
    output = ""
    for line in xspf_file:
        output = output + line
    print output.rstrip('\n')
    
# Optionen zuweisen, die später ausgewertet werden sollen/können.

parser = OptionParser(version="%prog 0.10", 
                      usage="usage: %prog [options]")

#parser.set_defaults(verbose=False)

parser.add_option("-v", "--verbose", action="store_true",  
                  help="Enable verbose output")
parser.add_option("-o","--vorbis", help="Normal Vorbiscomment (Deprecated)", 
                  action="callback", callback=print_vorbis)
parser.add_option("-p", "--plain",  
                  help="Vorbiscomment-like but for internal use", 
                  action="callback", callback=print_plain)
parser.add_option("-s", "--stream", help="Vorbiscomment for Stream (Deprecated)", 
                  action="callback", callback=print_stream)
parser.add_option("-a", "--artist", help="Only current Artist",  
                  action="callback", callback=print_current_artist)
parser.add_option("-t", "--title", help="Only current Title",  
                  action="callback", callback=print_current_title)
parser.add_option("-x", "--xspf-track",  
                  help="XSPF <track/>-Element for Playlist",  
                  action="callback", callback=print_xspf)
# Option-Parser starten und Kommandozeilen-Optionen auslesen 
(option, args) = parser.parse_args()

DEBUG=option.verbose

