#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"Usage: %s -P <port>"
from socket import *
from pickle import *
from sys import *
import struct
import time
import os

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

def read_request(filename):
	path_name = "/home/raulbs/Documentos/"+filename
	if os.path.isfile(path_name):
		f=open(path_name,'rb')
		bytestosend = f.read(1024)
		sock.sendto(bytestosend, client)
		while bytestosend != "":

			bytestosend = f.read(1024)
			sock.sendto(bytestosend, client)


def write_request(filename):
	print("adsfsdf")

initialization_handler()
port = int(argv[2])
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('', port))
n = 0

while 1:
	msg, client = sock.recvfrom(1024)
	n += 1
	request_handler(sock, msg, client, n)
sock.close()	
