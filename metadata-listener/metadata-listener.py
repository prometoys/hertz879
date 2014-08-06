#!/usr/bin/python
# -*- coding: utf8 -*-
import socket, re, sys, errno
from datetime import datetime
from optparse import OptionParser

# Dieses Skript lauscht auf Now-and-Next Nachrichten von Rivendell, die
# Angaben über das gerade gespielte Event (Song, Jingle, Beitrag, …) enthalten.
# Rivendell sendet per UDP. Daher Port und IP vom lauschenden Rechner angeben.

# TODO: Akzeptiert auch hostnamen, prüfen, ob IP/Host zum eigenen System gehört
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

# TODO: Dateiname via Variable

XSPF_FRAGMENT_FILENAME='tmp/xpsf-current-fragment'

# Optionen zuweisen, die später ausgewertet werden sollen/können.

parser = OptionParser(version="%prog 0.10", 
                      usage="usage: %prog [options]")

parser.set_defaults(verbose=False)
parser.set_defaults(port=UDP_PORT)
parser.set_defaults(ip=UDP_IP)

parser.add_option("-p", "--port", dest="port", type="int", help="Port to listen")
parser.add_option("-i", "--ip", dest="ip", help="IP (v4) to listen")
parser.add_option("-v", "--verbose", action="store_true", 
                  help="Enable verbose output")

# Option-Parser starten und Kommandozeilen-Optionen auslesen 
(option, args) = parser.parse_args()

DEBUG=option.verbose
UDP_IP=option.ip
UDP_PORT=option.port

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

def error_print(string):
    print >> sys.stderr, string

def debug(string):
    if DEBUG:
        error_print(string)

# Hier lauscht das Skript konkret auf der angegebenen IP/PORT
# TODO: IPv6 ?? -> Kann Rivendell nicht.
# TODO: Exception-Handling: IP/Port (keine IP, Socket schon in Benutzung etc)

#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
#sock.bind((UDP_IP, UDP_PORT))

if UDP_IP=="":
    UDP_STRING= '*:'+`UDP_PORT`
else:
    UDP_STRING= UDP_IP+':'+`UDP_PORT`

try:
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
except socket.error, e:
    SOCK_ERR_STR = "[" + UDP_STRING +"]: "
    errorcode=e[0]
    errordesc=e[1]
    # TODO: Fehler, die nicht zu einem exit führen sollen, sind hier nicht vorgesehen
    # Sonst sys.exit in die entsprechenden if-teile reinverschieben.
    if errorcode == errno.EACCES:
        error_print(SOCK_ERR_STR + errordesc)
    elif errorcode == errno.EADDRINUSE:
        error_print(SOCK_ERR_STR + errordesc)
        # Spezieller Exitcode für die Bash, damit wir in dem Fall warten können.
        sys.exit(5)
    elif errorcode == socket.EAI_NODATA:
         error_print(SOCK_ERR_STR + errordesc)
    else:
        error_print(SOCK_ERR_STR + " Error " + `errorcode` + "], " + errordesc)
    sys.exit(1)
except OverflowError, e:
    # Wir wollen nur die Beschreibung "port must be 0-65535" aus
    # OverflowError('getsockaddrarg: port must be 0-65535.',)
    errordesc=e[0].split("'")[0].split(":")[1]
    error_print("["+UDP_STRING + "]: " + errordesc)
    sys.exit(1)

# Variablen die zur Auswertung benötigt werden
artist = ""
song = ""
group = ""
ms = ""

# Dauerschleife, für jedes eingehende Paket wird sie einmal durchlaufen
while True:
    try:
        debug('Listening on '+UDP_STRING) 
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        debug('Received message from '+ `addr` + ': ' + data )
        
        # Empfangene Zeichenkette aufteilen.
        try:
            group, artist, song, ms = data.rstrip('\n').split(SPLIT_CHAR)
        except ValueError:
            error_print("Ignoring packet with wrong value format: " + data)
        
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
            xmltitle = "\t<title>"+song+"</title>\n"
            xmlcreator = "\t<creator>"+artist+"</creator>\n"
            xmlduration = "\t<duration>"+ms+"</duration>\n"
            xmlmeta = "\t<meta rel=\""+XSPF_META_TIMESTAMP_STRING+"\">"+date+"</meta>\n"
            xmltrack = "<track>\n" + xmltitle + xmlcreator + xmlduration + xmlmeta + "</track>"
            
            # TODO: Plain Ausgabe
            
            try:
                outputfile = open(XSPF_FRAGMENT_FILENAME, 'a')
                outputfile.write(track)
                #TODO: nur das Kind-Element track in die Datei schreiben
                outputfile.close()
            except IOError, e:
                # TODO: Ordner erstellen, Datei erzeugen
                print `e`
                sys.exit(1)
            
            
            # TODO: Ausgabe optional (optparse?)
            # XML-Codeschnipsel ausgeben.
            print track
            
            # Variablen leeren, insbesondere group, da es für "if" genutzt wird
            track = ""
            group = ""

        else:
            pass
            debug("Excluding GROUP: _" + group + "_")
    except KeyboardInterrupt:
        debug("\nExit listener by user interrupt.")
        exit(0)


