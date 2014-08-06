#!/usr/bin/python
# -*- coding: utf8 -*-
import socket, re
from datetime import datetime
from optparse import OptionParser

# Dieses Skript lauscht auf Now-and-Next Nachrichten von Rivendell, die
# Angaben über das gerade gespielte Event (Song, Jingle, Beitrag, …) enthalten.
# Rivendell sendet per UDP. Daher Port und IP vom lauschenden Rechner angeben.


# UDP_IP:
# -------
# IP des Netzwerk-Devices, auf dem nach Now&Next-Paketen gelauscht werden soll.
# Nur lokal lauschen (nur zum testen sinnvoll)
# UDP_IP = "127.0.0.1" 
#
# Auf allen Netzwerk-Geräten lauschen
# UDP_IP = ""
#
# Vorgabe: IP des Netzwerk-Devices, was die Verbindung zwischen Studio- und 
# Streamrechner erstellt. 

# UDP_IP = "129.70.176.39"

UDP_IP = ""

# UDP_PORT:
# ---------
# Port auf dem die Nachrichten via UDP eingehen. Den Port nachsehen in Rivendell 
# unter: rdadmin -> Manage Hosts -> Studio-Rechner -> RDAirplay -> Now&Next Data
#
# Vorgabe: 5000

UDP_PORT = 5000


# WANTED_GROUPS:
# --------------
# Welche Gruppen sollen in die Plylist eingebunden werden? Namen in Rivendell
# nachsehen in rdadmin -> Manage Groups
# Groß- und Kleinschreibung beachten.

WANTED_GROUPS = ["MUSIC", "MusikArchiv", "WORT", "TRAFFIC", "SHOWS"]


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

DEBUG=option.verbose

#TODO: Von .hirse.rc Variablen lesen


#TODO: Haverie-System / Restart Listener (while true??)


# SPLIT_CHAR:
# -----------
# Zeichen, welches die einzelnen Felder trennt. Gnaues Format den 
# Now&Next-Einstellungen entnehmen. Derzeit: 
#
# "%g|%a|%t|%h %r"
# 
# %g = group, %a = artist, %t = track, %h = dauer in ms, %r = Zeilenumbruch

SPLIT_CHAR = "|"

# XSPF_META_TIMESTAMP_STRING:
# ---------------------------
# Zeichenkette, für die Metadaten in der Playliste. Arg unwichtig.
XSPF_META_TIMESTAMP_STRING="http://radio.uni-bielefeld.de/xspf/timestamp"


# Debug-Funktion
#TODO: Ausgabe auf stderr?
def debug(string):
    if DEBUG:
        print string

# Hier lauscht das Skript konkret auf der angegebenen IP/PORT
# TODO: IPv6 ?? -> Kann Rivendell nicht.
# TODO: Exception-Handling: IP/Port (keine IP, Socket schon in Benutzung etc)
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

# Variablen die zur Auswertung benötigt werden
artist = ""
song = ""
group = ""
ms = ""

# Dauerschleife, für jedes eingehende Paket wird sie einmal durchlaufen
while True:    
    debug('listening on '+UDP_IP+':'+`UDP_PORT`) 
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    debug('received message from '+ `addr` + ': ' + data )
    
    # Empfangene Zeichenkette aufteilen.
    group, artist, song, ms = data.rstrip('\n').split(SPLIT_CHAR)
    
    # Zeichenketten von Leerzeichen etc. säubern.
    artist = artist.strip()
    song = song.strip()
    group = group.strip()
    ms = ms.strip()
    # TODO: Zeitzone korrekt ermitteln und einbinden
    date = datetime.today().strftime("%Y-%m-%dT%H:%M:%S+01:00")
    
    # Nur die Events in die Playlist einpflegen, die wir oben angegeben haben.
    if group in WANTED_GROUPS:
        # XML von Hand bauen. Für das bissl XSPF lohnt sich keine lib.
        # Es gibt xspf.py, aber das hat <meta> noch nicht implementiert.
        title = "\t<title>"+song+"</title>\n"
        creator = "\t<creator>"+artist+"</creator>\n"
        duration = "\t<duration>"+ms+"</duration>\n"
        meta = "\t<meta rel=\""+XSPF_META_TIMESTAMP_STRING+"\">"+date+"</meta>\n"
        track = "<track>\n" + title + creator + duration + meta + "</track>"
        
        # XML-Codeschnipsel ausgeben.
        print track
        
        # Variablen leeren, insbesondere group, da es für "if" genutzt wird
        track = ""
        group = ""

    else:
        pass
        debug("Excluding GROUP: _" + group + "_")


