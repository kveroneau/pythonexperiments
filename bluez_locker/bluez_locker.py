#!/usr/bin/python

from bluetooth import *
import subprocess, os, sys

DAEMON = False
if sys.argv.pop() == '-d':
    DAEMON = True
    pid = os.fork()
    if pid > 0:
        print "Forked process: %d" % pid
        sys.exit(0)

if DAEMON:
    null = open(os.devnull, 'r+')
    sys.stdout = null
    sys.stderr = null

hostname = open('/etc/hostname', 'r').read().replace('\n', '')

server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",7))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "457807c0-4897-11df-9879-0800200c9a66"

advertise_service( server_sock, "SL4A",
                   service_id = uuid,
                   service_classes = [ uuid ],
                   profiles = []
                   )

try:
    while True:
        print "Waiting for connection on RFCOMM channel %d" % port
        client_sock, client_info = server_sock.accept()
        print "Accepted connection from ", client_info
        data = client_sock.recv(1024)
        if data == 'LOCK':
            subprocess.call(['screens-lock'])
            client_sock.send('%s has been locked!\n' % hostname)
        elif data == 'UNLOCK':
            subprocess.call(['screens-unlock'])
            client_sock.send('%s has been unlocked!\n' % hostname)
        print "disconnected"
        client_sock.close()
except:
    server_sock.close()
    print "all done"
