#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"Usage: %s <server> <port>"
from socket import *
from pickle import *
from sys import *
import struct

if len(argv) != 3:
	print(__doc__ % argv[0])
	exit(1)

sock = socket(AF_INET, SOCK_DGRAM)

while 1:
	data = struct.pack('=2h',0,1)
	# ends with ''

	sock.sendto(data, (argv[1], int(argv[2])))
	msg, server = sock.recvfrom(1024)
	print("Reply is '%s'" % msg.decode())

sock.close()
