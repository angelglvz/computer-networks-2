#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"Usage: %s -S <server> -P <port>"
from socket import *
from pickle import *
from sys import *
import struct


def initialization_handler():
	if len(argv) != 5:
		print(__doc__ % argv[0])
		exit(1)
	if argv[1].lower() != "-s":
		print(__doc__ % argv[0])
		exit(1)
	if argv[3].lower() != "-p":
		print(__doc__ % argv[0])
		exit(1)	

def analyze(command):
	sending = command.split()
	if sending[0].lower() == "read":
		if len(sending) == 1: exit(1)
		fileName = sending[1].encode()
		mode = b'NETASCII'
		data = struct.pack('!H'+str(len(fileName))+'sB'+str(len(mode))+'sB', 1, fileName, 0,mode, 0)
		# ends with ''
		sock.sendto(data, (destination, port))
	elif sending[0].lower() == "write":
		if len(sending) == 1: exit(1)
		fileName = args[1].encode()
		mode = b'NETASCII'
		data = struct.pack('!H'+str(len(fileName))+'sB'+str(len(mode))+'sB', 2, fileName, 0,mode, 0)
		# ends with ''
		sock.sendto(data, (destination, port))
	elif sending[0].lower() == "quit":
		exit(1)
	else:
		print("""\
The operation introduced is not correct. The available operations are:
	- read <file>
	- write <file>
	- quit
		""")


initialization_handler()
destination = argv[2]
port = int(argv[4])
sock = socket(AF_INET, SOCK_DGRAM)

while 1:
	command = input('TFTP@UDP> ')

	if not command: break
	analyze(command)
	msg, server = sock.recvfrom(1024)
	print(msg.decode())

sock.close()
