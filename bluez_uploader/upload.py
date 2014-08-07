#!/usr/bin/python

from bluetooth import *
import sys

if len(sys.argv) != 2:
    print "Please enter a file name as a parameter."
    sys.exit(0)

fname = sys.argv[1]

addr = '00:00:00:00:00:00'
uuid = '457807c0-4897-11df-9879-0800200c9a66'

print "Searching for service..."
service_matches = find_service( uuid = uuid, address = addr )
if len(service_matches) == 0:
    print "couldn't find the service =("
    sys.exit(0)

first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

print "connecting to \"%s\" on %s port %s" % (name, host, port)
sock=BluetoothSocket( RFCOMM )
sock.connect((host, port))

print "connected.  Sending file data..."
sock.send('%s\n' % fname)
data = open(fname,'r').read()
sock.send('%s\n' % len(data))
sock.send(data)
print "Closing."
sock.close()
