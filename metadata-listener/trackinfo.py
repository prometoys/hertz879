#!/usr/bin/python
# -*- coding: utf8 -*-
import socket, re
from optparse import OptionParser



# Methoden, die vom OptionParser aufgerufen werden sollen
# auslagern in neues trackinfo?
def print_vorbis(option, opt, value, parser):
    print option, opt, value, parser

def print_plain(option, opt, value, parser):
    print option, opt, value, parser

def print_stream(option, opt, value, parser):
    print option, opt, value, parser

def print_current_artist(option, opt, value, parser):
    print option, opt, value, parser

def print_current_title(option, opt, value, parser):
    print option, opt, value, parser

def print_xspf(option, opt, value, parser):
    print option, opt, value, parser

# Optionen zuweisen, die später ausgewertet werden sollen/können.

parser = OptionParser(version="%prog 0.10", 
                      usage="usage: %prog [options]")

parser.set_defaults(verbose=False)

parser.add_option("-o","--vorbis", help="Normal Vorbiscomment", 
                  action="callback", callback=print_vorbis)
parser.add_option("-p", "--plain",  
                  help="Vorbiscomment-like but for internal use", 
                  action="callback", callback=print_plain)
parser.add_option("-s", "--stream", help="Vorbiscomment for Stream", 
                  action="callback", callback=print_stream)
parser.add_option("-a", "--artist", help="Only current Artist",  
                  action="callback", callback=print_current_artist)
parser.add_option("-t", "--title", help="Only current Title",  
                  action="callback", callback=print_current_title)
parser.add_option("-x", "--xspf-track",  
                  help="XSPF <track/>-Element for Playlist",  
                  action="callback", callback=print_xspf)
parser.add_option("-v", "--verbose", action="store_true",  
                  help="Enable verbose output")

# Option-Parser starten und Kommandozeilen-Optionen auslesen 
(option, args) = parser.parse_args()

