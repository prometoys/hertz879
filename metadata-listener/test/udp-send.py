#!/usr/bin/python
# -*- coding: utf8 -*-
from __future__ import print_function
from __future__ import unicode_literals 
import socket
import random
import os
from optparse import OptionParser

# 

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))+"/"
FILE=SCRIPT_DIR+'playlist.txt'
UDP_IP = "127.0.0.1"
UDP_PORT = 5000
MESSAGE = "GROUP|ARTIST|TITLE|123456| \n"

parser = OptionParser(version="%prog 0.10", 
                      usage="usage: %prog [options]")

#parser.set_defaults(verbose=False)
parser.set_defaults(port=UDP_PORT)
parser.set_defaults(ip=UDP_IP)
parser.set_defaults(message="")
parser.set_defaults(filename=FILE)
parser.set_defaults(random=True)

parser.add_option("-p", "--port", dest="port", type="int", help="Port to send")
parser.add_option("-i", "--ip", dest="ip", help="IP (v4) to send")
parser.add_option("-m", "--message", dest="message", help="Message to send")
parser.add_option("-u", "--utf8", dest="unicode", action="store_true", 
                  help="Send with UTF-8 encoding")
parser.add_option("-n", "--no-random", dest="random", action="store_false", 
                  help="Enable random select (conflict with -f)")
#TODO: Konflikt zwischen -n und -f einbauen
parser.add_option("-f", "--filename", dest="filename", help="Playlist-file to pick a random line to send")
#parser.add_option("-v", "--verbose", action="store_true", 
#                  help="Enable verbose output")

# Option-Parser starten und Kommandozeilen-Optionen auslesen 
(option, args) = parser.parse_args()


if(len(option.message)>0):
    MESSAGE=option.message
    option.random=False

#DEBUG=option.verbose
UDP_IP=option.ip
UDP_PORT=option.port


file = open(option.filename,'rU')

list = []

if(option.random):
    for line in file:
        list.append( line.decode('utf-8').rstrip('\n'))
    MESSAGE = list[random.randrange(len(list))]

print("UDP target IP:", UDP_IP)
print("UDP target port:", UDP_PORT)
print( "message:", MESSAGE)

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
if(option.unicode):
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
else:
    sock.sendto(MESSAGE.decode("utf-8").encode("iso-8859-15"), (UDP_IP, UDP_PORT))

