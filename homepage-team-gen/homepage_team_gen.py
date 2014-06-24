#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv, re
from unidecode import unidecode

# import_file_name:
# Team-Liste zum importieren, erwartet wird eine Datei, die die 
# Namen in folgender Form je Zeile enthält: 
# "Nachname;Vorname;Foto-Link;Foto-mit-Text-Link"


import_file_name = "foto-liste.csv"

# output_file_name:
# Ausgabe-Datei, in die der fertige HTML-Code geschrieben wird.

output_file_name = "ausgabe.txt"

# Debug-Ausgaben aktivieren, um Fehler zu identifizieren
# True zum einschalten, False zum deaktivieren
DEBUG=True

# sort_key:
# Redakteure Sortieren nach Vorname oder Nachname
# Vorname: 1, Nachname: 0
sort_key = 1


##################################################
# Hier beginnt das eigentliche Skript            #
##################################################

# Funktion um Debug-Ausgaben zu steuern. Derzeit nur simple 
# Ausgabe im Terminal. Ausbaufähig

def debug(string):
	if DEBUG:
		print string

# Dateien werden geöffnet, zum lesen... 
importfile = csv.reader(open(import_file_name,'rU'), delimiter=';', quotechar='"')

# ...bzw. schreiben
outputfile = open(output_file_name, 'w')

# Inhalt der Team-Datei wird in eine Liste umgewandelt.
# (Das ginge auch kompakter, hier ausführlich für die bessere
# Lesbarkeit)

data = list(importfile)

# Zähler, um die einzelnen Spalten zu erzeugen
count = 1

# Leere Variable, in der das Ergebnis gespeichert wird.
html_output=""

# Kommentarzeilen aus der Liste entfernen
data = [x for x in data if not x[0].strip().startswith("#")]


# Unnötige Leerzeichen entfernen
for line in data:	
	for i in range(len(line)):
		line[i] = line[i].strip()
		debug("stripped-"+line[i]+"-")

# Liste sortieren, bevor sie abgearbeitet wird
def getKey(item):
	debug(item)
	debug(len(item))
	return item[1]

data = sorted(data, key=getKey)

# HTML-String zusammenbauen

def html_gen(name_string, photo_url, photo_with_name_url):

	html='<a href="http://www.radiohertz.de/beta-site/REDAKTEURNAME/"> <img src="FOTO-LINK" onmouseover="this.src=\'FOTO-TEXT-LINK\'"onmouseout="this.src =\'FOTO-LINK\'" /></a>'

	html = html.replace("REDAKTEURNAME", name_string)
	html = html.replace("FOTO-LINK", photo_url)
	html = html.replace("FOTO-TEXT-LINK", photo_with_name_url)
	return html

# Zeichenkette von Leerzeichen und mehr befreien
def string_cleaner(string):

	# Zeichenkette in ein Unicode-Objekt verwandeln
	ustring = unicode(string,encoding="utf_8")

	# Zeichenkette von Umlauten und Leerzeichen in Bindestriche umwandeln
	result = unidecode(ustring.strip().replace (" ", "-").lower())

	return result


# Liste mit den Redakteuren wird Zeile für Zeile abgearbeitet
for line in data:

	lastname, firstname, photo_url, photo_with_name_url = line[0], line[1], line[2], line[3],
	debug("vorname: " + firstname + "\nnachname: " + lastname + "\nfoto-link: " + photo_url + "\ntext-link: " + photo_with_name_url + "\n-------------------")
	
	name_string = string_cleaner(firstname)+"-"+string_cleaner(lastname)
	
	if count < 3:
		html_output=html_output+html_gen(name_string, photo_url, photo_with_name_url)
		count+=1
	elif count >= 3:
		html_output=html_output+html_gen(name_string, photo_url, photo_with_name_url)+"\n\n"
		count=1

# Daten schreiben in Ausgabedatei und diese schliessen.
outputfile.write(html_output)
outputfile.close()
