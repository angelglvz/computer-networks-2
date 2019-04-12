#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"Usage: %s -S <server> -P <port>"
from socket import *
from pickle import *
from sys import *
import struct
import math
import os
import time

modes = {
	0: "NETASCII"
} 
server_error_msg = {
    0: "Not defined, see error message (if any).",
    1: "File not found.",
    2: "Access violation.",
    3: "Disk full or allocation exceeded.",
    4: "Illegal TFTP operation.",
    5: "Unknown transfer ID.",
    6: "File already exists.",
    7: "No such user."
}

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
		fileName = sending[1]
		
		data = struct.pack('!H'+str(len(fileName))+'sB'+str(len(modes[0]))+'sB', 1, fileName.encode(), 0,modes[0].encode(), 0)
		# ends with ''
		sock.sendto(data, (destination, port))
		receive_data(fileName)

	elif sending[0].lower() == "write":
		if len(sending) == 1: exit(1)
		fileName = sending[1]
		
		data = struct.pack('!H'+str(len(fileName))+'sB'+str(len(modes[0]))+'sB', 2, fileName.encode(), 0,modes[0].encode(), 0)
		# ends with ''
		sock.sendto(data, (destination, port))
		send_data(fileName)
	elif sending[0].lower() == "quit":
		exit(1)
	else:
		print("""\
The operation introduced is not correct. The available operations are:
	- read <file>
	- write <file>
	- quit
		""")

def receive_data(filename):
	path_name = "/home/raulbs/Descargas/"+filename
	f=open(path_name,'w')
	pack = 1
	try:
		msg, server = sock.recvfrom(1024)
	
	except socket.timeout:
		data = struct.pack('!H'+str(len(fileName))+'sB'+str(len(modes[0]))+'sB', 1, fileName.encode(), 0,modes[0].encode(), 0)
		# ends with ''
		sock.sendto(data, (destination, port))
		receive_data(filename)
	else:
		op = struct.unpack("!H", msg[0:2])[0]
		
		if op == 3:
			pack = struct.unpack("!H", msg[2:4])[0]
			pack += 1
			size = len(msg)
			dataLen = size - 4
			data = struct.unpack("!"+str(dataLen)+"s", msg[4:size])[0]
			print(data.decode())
			f.write(data.decode())
			send_ack(pack)
		else:
			print("There was an error in the receiving packets\n")
			return

	while 1:
		try:
			msg, server = sock.recvfrom(1024)
		
		except socket.timeout:
			send_ack(pack)
			continue
		else:
			op = struct.unpack("!H", msg[0:2])[0]
		
			if op == 3:
				pack = struct.unpack("!H", msg[2:4])[0]
				pack += 1
				size = len(msg)
				dataLen = size - 4
				data = struct.unpack("!"+str(dataLen)+"s", msg[4:size])[0]
				print(data.decode())
				f.write(data.decode())
				send_ack(pack)
			else:
				print("There was an error in the receiving packets\n")
				break
		
def send_ack(number):
	ack_msg = struct.pack('!HH', 4, number)
	sock.sendto(ack_msg, (destination,port))

def error_server(msg):
	error_code = struct.unpack("!H", msg[2:4])[0]
	error_string_end = msg.find(0, 4)
	error_string_len = error_string_end - 4
	error_string = struct.unpack("!"+str(error_string_len)+"s", msg[4:error_string_end])[0].decode()
	print('Error ',error_code,': ',error_string)

def send_data(filename):
	path_name = "/home/raulbs/Descargas/"+filename
	if os.path.isfile(path_name):
		size = os.path.getsize (path_name) 
		num_packs = math.ceil(size/512)
		print(size)
		print(num_packs)
		pack = 0
		f=open(path_name,'rb')
		
		try:
			msg, server = sock.recvfrom(1024)

		except socket.timeout:
			data = struct.pack('!H'+str(len(fileName))+'sB'+str(len(modes[0]))+'sB', 2, fileName.encode(), 0,modes[0].encode(), 0)
			# ends with ''
			sock.sendto(data, (destination, port))
			send_data(fileName)
		else:
			op = struct.unpack("!H", msg[0:2])[0]
			if op == 4:
				pack = struct.unpack("!H", msg[2:4])[0]
				bytestosend = f.read(512)
				data = struct.pack('!HH'+str(len(bytestosend))+'s', 3, pack, bytestosend)
				sock.sendto(data, (destination,port))
				num_packs -= 1
			elif op == 5:
				error_server(msg)
				return
			else:
				print("There was an error in the receiving ACK\n")
				return

		while num_packs:
			try:
				msg, server = sock.recvfrom(1024)

			except socket.timeout:
				sock.sendto(data, (destination,port))
				continue
			else:
				op = struct.unpack("!H", msg[0:2])[0]
				if op == 4:
					pack = struct.unpack("!H", msg[2:4])[0]
					bytestosend = f.read(512)
					data = struct.pack('!HH'+str(len(bytestosend))+'s', 3, pack, bytestosend)
					num_packs -= 1
					sock.sendto(data, (destination,port))
				
				elif op == 5:
					error_server(msg)
					break
				else:
					print("There was an error in the receiving ACK\n")
					break
			
initialization_handler()
destination = argv[2]
port = int(argv[4])
sock = socket(AF_INET, SOCK_DGRAM)

while 1:
	
	command = input('TFTP@UDP> ')

	if not command: break
	
	order(command)
	

sock.close()

