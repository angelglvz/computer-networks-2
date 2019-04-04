#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"Usage: %s -P <port>"
from socket import *
from pickle import *
from sys import *
import struct
import time
import os

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
	time.sleep(1)
	op = struct.unpack("!H", msg[0:2])[0]
	filenameEnd = msg.find(0, 2)
	filenameLen = filenameEnd - 2
	filename = struct.unpack("!"+str(filenameLen)+"s", msg[2:filenameEnd])[0].decode()
	modeEnd = msg.find(0, filenameEnd+1)
	modeLen = modeEnd - (filenameEnd + 1)
	mode = struct.unpack("!"+str(modeLen)+"s", msg[filenameEnd+1:modeEnd])[0].decode()
	option_handler(op, filename)

def option_handler(option, filename):
	if option == 1:
		read_request(filename)
	elif option == 2:
		write_request(filename)
	else:
		print("There is an error in the request of the client.")

def send_ack():
	ack_msg = struct.pack('!HH', 4, 0)
	sock.sendto(ack_msg, client)

def send_error(code):
	error_string = server_error_msg[code].encode()
	error_msg = struct.pack('!HH'+str(len(error_string))+'sB', 5, code, error_string, 0)
	sock.sendto(error_msg, client)

def read_request(filename):
	path_name = "/home/raulbs/Documentos/"+filename
	if os.path.isfile(path_name):
		f=open(path_name,'rb')
		bytestosend = f.read(100)
		sock.sendto(bytestosend, client)
	else:
		send_error(1)

def write_request(filename):
	path_name = "/home/raulbs/Documentos/"+filename
	if os.path.isfile(path_name):
		send_error(1)
	else:
		send_ack()

initialization_handler()
port = int(argv[2])
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('', port))
n = 0

while 1:
	msg, client = sock.recvfrom(1024)
	n += 1
	#request_handler(sock, msg, client, n)
sock.close()	
