#!/usr/bin/python
import socket
import random
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))+"/"

UDP_IP = "127.0.0.1"
UDP_PORT = 5000
MESSAGE = "GROUP|ARTIST|TITLE|123456 \n"

file = open(SCRIPT_DIR+'playlist.txt','rU')

list = []

for line in file:
	list.append( line.rstrip('\n'))

MESSAGE = list[random.randrange(len(list))]

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT
print "message:", MESSAGE

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
