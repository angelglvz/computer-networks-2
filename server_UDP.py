#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"Usage: %s -P <port>"
import socket 
from sys import *
import struct
import time
import os
import math

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
	if len(argv)!= 3:
		print(__doc__ % argv[0])
		exit(1)
	if argv[1].lower() != "-p":
		print(__doc__ % argv[0])
		exit(1)

def request_handler(sock, msg, client, n):
	print('New request: ', n, client)
	op = struct.unpack("!H", msg[0:2])[0]

	if op == 1:
		filenameEnd = msg.find(0, 2)
		filenameLen = filenameEnd - 2
		filename = struct.unpack("!"+str(filenameLen)+"s", msg[2:filenameEnd])[0].decode()
		modeEnd = msg.find(0, filenameEnd+1)
		modeLen = modeEnd - (filenameEnd + 1)
		mode = struct.unpack("!"+str(modeLen)+"s", msg[filenameEnd+1:modeEnd])[0].decode()
		read_request(filename, client)
	elif op == 2:
		filenameEnd = msg.find(0, 2)
		filenameLen = filenameEnd - 2
		filename = struct.unpack("!"+str(filenameLen)+"s", msg[2:filenameEnd])[0].decode()
		modeEnd = msg.find(0, filenameEnd+1)
		modeLen = modeEnd - (filenameEnd + 1)
		mode = struct.unpack("!"+str(modeLen)+"s", msg[filenameEnd+1:modeEnd])[0].decode()
		write_request(filename)
	else:
		print("There is an error in the request of the client.")

def send_data_pack(bytestosend, pack):
	data = struct.pack('!HH'+str(len(bytestosend))+'s', 3, pack, bytestosend)
	print("Sending to client: PACK ",pack)
	sock.sendto(data, client)
def send_ack(number):
	ack_msg = struct.pack('!HH', 4, number)
	print("Sending to client: ACK ",number)
	sock.sendto(ack_msg, client)

def send_error(code):
	error_string = server_error_msg[code].encode()
	error_msg = struct.pack('!HH'+str(len(error_string))+'sB', 5, code, error_string, 0)
	print("Sending to client: ERROR ",code," (",server_error_msg[code])
	sock.sendto(error_msg, client)

def read_request(filename, client):
	path_name = "/home/raulbs/Documentos/"+filename
	if os.path.isfile(path_name):
		size = os.path.getsize (path_name) 
		num_packs = math.ceil(size/512)
		pack = 0
		f=open(path_name,'rb')
		bytestosend = f.read(512)

		while 1:
			try:
				send_data_pack(bytestosend, pack)
				msg, client = sock.recvfrom(1024)
			except socket.error:
				continue
			else:
				op = struct.unpack("!H", msg[0:2])[0]
				if op == 4:
					packReceived = struct.unpack("!H", msg[2:4])[0]
					print("Receiving from client: ACK ", packReceived)
					if packReceived == (pack + 1):
						if num_packs == pack + 1:
							break
						else:
							bytestosend = f.read(512)
							pack += 1
				elif op == 5:
					error_server(msg)
					break
				elif op == 1:
					continue
				else:
					print("There was an error in the receiving ACK\n")
					break
				
	else:
		send_error(server_error_msg[1])

def write_request(filename):
	path_name = "/home/raulbs/Documentos/"+filename
	if os.path.isfile(path_name):
		send_error(server_error_msg[6])
	else:
		f=open(path_name,'wb')
		pack = 0
		while 1:
			try:
				send_ack(pack)
				msg, client = sock.recvfrom(1024)
				
			except socket.error:
				continue
			else:
				op = struct.unpack("!H", msg[0:2])[0]
			 
				if op == 3:
					packReceived = struct.unpack("!H", msg[2:4])[0]
					print("Receiving from client: PACK ", packReceived)
					if pack == packReceived:
						pack += 1
						size = len(msg)
						dataLen = size - 4
						data = struct.unpack("!"+str(dataLen)+"s", msg[4:size])[0]
						f.write(data)
						if len(data) < 512:
							send_ack(pack)
							return
				elif op == 2:
					continue
				else:
					print("There was an error in the receiving packets\n")
					break

initialization_handler()
port = int(argv[2])
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', port))
sec = 1
usec = 10000
timevalue = struct.pack('ll', sec, usec)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timevalue)
n = 0

while 1:
	try:
		msg, client = sock.recvfrom(1024)
		n += 1
		request_handler(sock, msg, client, n)
	except socket.error:
		continue
sock.close()	
