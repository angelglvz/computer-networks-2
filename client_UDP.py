#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"Usage: %s -S <server> -P <port>"
import socket
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

TFTP_OPCODES = {
    'unknown': 0,
    'read': 1,  # RRQ
    'write': 2,  # WRQ
    'data': 3,  # DATA
    'ack': 4,  # ACKNOWLEDGMENT
    'error': 5}  # ERROR


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
		send_read_request(fileName)
		receive_data(fileName)

	elif sending[0].lower() == "write":
		if len(sending) == 1: exit(1)
		fileName = sending[1]
		send_write_request(fileName)
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
	start_time = time.time()
	path_name = "/home/angel/carpeta_publica_para_redes/cliente/"+filename
	if os.path.isfile(path_name):
		print('Error ',6,': ',server_error_msg[6])
	else:
		f=open(path_name,'w')
		pack=0

		try:
			msg, server = sock.recvfrom(1024)
		except socket.error:
			send_read_request(filename)
		else:
			op = struct.unpack("!H", msg[0:2])[0]
			
			if op == 3:
				packReceived = struct.unpack("!H", msg[2:4])[0]
				print("Receiving from server: PACK ", packReceived)
				if pack == packReceived:
					pack += 1
					size = len(msg)
					dataLen = size - 4
					data = struct.unpack("!"+str(dataLen)+"s", msg[4:size])[0]
					f.write(data.decode())
			elif op == 5:
				error_server(msg)
				return
			else:
				print("There was an error in the receiving packets\n")
				return

		while 1:
			try:
				send_ack(pack)
				msg, server = sock.recvfrom(1024)
		
			except socket.error:
				if pack == 0:
					send_read_request(filename)
			else:
				op = struct.unpack("!H", msg[0:2])[0]
		
				if op == 3:
					packReceived = struct.unpack("!H", msg[2:4])[0]
					print("Receiving from server: PACK ", packReceived)
					if pack == packReceived:
						pack += 1
						size = len(msg)
						dataLen = size - 4
						data = struct.unpack("!"+str(dataLen)+"s", msg[4:size])[0]
						f.write(data.decode())
						if len(data) < 512:
							send_ack(pack)
							return
				elif op == 5:
					error_server(msg)
					break
				else:
					print("There was an error in the receiving packets\n")
					break
	print("--- %s seconds ---" % (time.time() - start_time))

def send_write_request(filename):
	data = struct.pack('!H'+str(len(filename))+'sB'+str(len(modes[0]))+'sB', TFTP_OPCODES['write'], filename.encode(), 0,modes[0].encode(), 0)
		# ends with ''
	sock.sendto(data, (destination, port))

def send_read_request(filename):
	data = struct.pack('!H'+str(len(filename))+'sB'+str(len(modes[0]))+'sB', TFTP_OPCODES['read'], filename.encode(), 0,modes[0].encode(), 0)
		# ends with ''
	sock.sendto(data, (destination, port))

def send_data_pack(bytestosend, pack):
	data = struct.pack('!HH'+str(len(bytestosend))+'s', TFTP_OPCODES['data'], pack, bytestosend)
	print("Sending to server: PACK ",pack)
	sock.sendto(data, (destination,port))

def send_ack(number):
	ack_msg = struct.pack('!HH', TFTP_OPCODES['ack'], number)
	print("Sending to server: ACK ",number)
	sock.sendto(ack_msg, (destination,port))

def error_server(msg):
	error_code = struct.unpack("!H", msg[2:4])[0]
	error_string_end = msg.find(0, 4)
	error_string_len = error_string_end - 4
	error_string = struct.unpack("!"+str(error_string_len)+"s", msg[4:error_string_end])[0].decode()
	print('Error ',error_code,': ',error_string)

def send_data(filename):
	start_time = time.time()
	path_name = "/home/angel/carpeta_publica_para_redes/cliente/"+filename
	if os.path.isfile(path_name):
		size = os.path.getsize (path_name) 
		num_packs = math.ceil(size/512)
		pack = 0
		f=open(path_name,'rb')
		
		try:
			msg, server = sock.recvfrom(1024)

		except socket.error:
			send_write_request(filename)
		else:
			op = struct.unpack("!H", msg[0:2])[0]
			if op == 4:
				packReceived = struct.unpack("!H", msg[2:4])[0]
				print("Receiving from server: ACK ", packReceived)
				bytestosend = f.read(512)
				pack += 1;
			elif op == 5:
				error_server(msg)
				return 
			else:
				print("There was an error in the receiving ACK\n")
				return

		while 1:
			try:
				send_data_pack(bytestosend, packReceived)
				msg, server = sock.recvfrom(1024)

			except socket.error:
				if pack == 0:
					send_write_request(filename)
			else:
				op = struct.unpack("!H", msg[0:2])[0]
				if op == 4:
					packReceived = struct.unpack("!H", msg[2:4])[0]
					print("Receiving from server: ACK ", packReceived)
					if packReceived == pack:
						if num_packs == pack:
							break
						else:
							bytestosend = f.read(512)
							pack += 1
					
				elif op == 5:
					error_server(msg)
					break
				else:
					print("There was an error in the receiving ACK\n")
					break

	else:
		print('Error ',1,': ',server_error_msg[1])
	print("--- %s seconds ---" % (time.time() - start_time))

		
initialization_handler()
destination = argv[2]
port = int(argv[4])
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sec = 1
usec = 10000
timevalue = struct.pack('ll', sec, usec)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timevalue)

while 1:
	
	command = input('TFTP@UDP> ')

	if not command: break
	
	order(command)
	

sock.close()

