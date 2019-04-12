#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"Usage: %s -P <port>"
from socket import *
from pickle import *
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

def send_ack(number):
	ack_msg = struct.pack('!HH', 4, number)
	sock.sendto(ack_msg, client)

def send_error(code):
	error_string = server_error_msg[code].encode()
	error_msg = struct.pack('!HH'+str(len(error_string))+'sB', 5, code, error_string, 0)
	sock.sendto(error_msg, client)

def read_request(filename, client):
	path_name = "/home/raulbs/Documentos/"+filename
	if os.path.isfile(path_name):
		size = os.path.getsize (path_name) 
		num_packs = math.ceil(size/512)
		print(size)
		print(num_packs)
		pack = 1
		f=open(path_name,'rb')
		bytestosend = f.read(512)
		print(bytestosend.decode())
		data = struct.pack('!HH'+str(len(bytestosend))+'s', 3, pack, bytestosend)
	

		while num_packs:
			try:
				sock.sendto(data, client)
				msg, client = sock.recvfrom(1024)
			except socket.timeout:
				continue
			else:
				op = struct.unpack("!H", msg[0:2])[0]
				print(op)
				if op == 4:
					pack = struct.unpack("!H", msg[2:4])[0]
					bytestosend = f.read(512)
					data = struct.pack('!HH'+str(len(bytestosend))+'s', 3, pack, bytestosend)
					num_packs -= 1
				elif op == 5:
					error_server(msg)
					break
				else:
					print("There was an error in the receiving ACK\n")
					break
				
	else:
		send_error(5)

def write_request(filename):
	path_name = "/home/raulbs/Documentos/"+filename
	if os.path.isfile(path_name):
		send_error(1)
	else:
		f=open(path_name,'w')
		pack = 0
		while 1:
			try:
				send_ack(pack)
				msg, client = sock.recvfrom(1024)
				
			except socket.timeout:
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
				elif op == 1:
					read_request(filename)
					break
				elif op == 2:
					write_request(filename)
					break
				else:
					print("There was an error in the receiving packets\n")
					break

initialization_handler()
port = int(argv[2])
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('', port))
sock.settimeout(20)
n = 0

while 1:
	msg, client = sock.recvfrom(1024)
	n += 1
	request_handler(sock, msg, client, n)
sock.close()	
