#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"Usage: %s -S <server> -P <port>"
from socket import *
from pickle import *
from sys import *
import struct
import math
import os



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

def order(command):
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
		fileName = sending[1].encode()
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

def analyze_msg():
	arguments = command.split()
	filename = arguments[1]

	while 1:

		msg, server = sock.recvfrom(1024)

		op = struct.unpack("!H", msg[0:2])[0]

		if op == 5:
			error_server(msg)
			break
	

def error_server(msg):
	error_code = struct.unpack("!H", msg[2:4])[0]
	error_string_end = msg.find(0, 4)
	error_string_len = error_string_end - 4
	error_string = struct.unpack("!"+str(error_string_len)+"s", msg[4:error_string_end])[0].decode()
	print('Error ',error_code,': ',error_string)

def send_data(filename):
	path_name = "~/Documentos/"+filename
	if os.path.isfile(path_name):
		size = os.path.getsize (path_name) 
		num_pack = math.ceil(size/1024)
		f=open(path_name,'rb')
		while num_pack:
			bytestosend = f.read(1024)
			#data = struct.pack('!H'+str(len(fileName))+'sB'+str(len(mode))+'sB', 1, fileName, 0,mode, 0)
			sock.sendto(bytestosend, (destination,port))
			num_pack -= 1
	else:
		print("You haven't this file: ",filename)

initialization_handler()
destination = argv[2]
port = int(argv[4])
sock = socket(AF_INET, SOCK_DGRAM)

while 1:
	
	command = input('TFTP@UDP> ')

	if not command: break
	send_data("servidor.py")
	#order(command)
	#analyze_msg()

sock.close()
