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

def main():
	initialization_handler()
	port = int(argv[2])
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(('0.0.0.0', port))
	sec = 4																		#Timeout of four seconds
	usec = 10000
	timevalue = struct.pack('ll', sec, usec)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timevalue)
	n = 0

	while 1:																	#It waits infinitly a request of some client.
		try:
			msg, client = sock.recvfrom(1024)
			n += 1
			request_handler(sock, msg, client, n)
		except socket.error:
			continue
	sock.close()


def initialization_handler():					#This method controls that the arguments we pass in the command
	if len(argv)!= 3:							#line is correct or not.
		print(__doc__ % argv[0])
		exit(1)
	if argv[1].lower() != "-p":
		print(__doc__ % argv[0])
		exit(1)

def request_handler(sock, msg, client, n):		#This method is used to the handling of the requests sent by the client.
	print('New request: ', n, client)
	op = struct.unpack("!H", msg[0:2])[0]

	if op == 1:
		filenameEnd = msg.find(0, 2)
		filenameLen = filenameEnd - 2
		filename = struct.unpack("!"+str(filenameLen)+"s", msg[2:filenameEnd])[0].decode()
		modeEnd = msg.find(0, filenameEnd+1)
		modeLen = modeEnd - (filenameEnd + 1)
		mode = struct.unpack("!"+str(modeLen)+"s", msg[filenameEnd+1:modeEnd])[0].decode()
		read_request(filename, client, sock)
	elif op == 2:
		filenameEnd = msg.find(0, 2)
		filenameLen = filenameEnd - 2
		filename = struct.unpack("!"+str(filenameLen)+"s", msg[2:filenameEnd])[0].decode()
		modeEnd = msg.find(0, filenameEnd+1)
		modeLen = modeEnd - (filenameEnd + 1)
		mode = struct.unpack("!"+str(modeLen)+"s", msg[filenameEnd+1:modeEnd])[0].decode()
		write_request(filename, client, sock)
	else:
		print("There is an error in the request of the client.")

def send_data_pack(bytestosend, pack,sock, client):			#This method is used to send a data pack with the number of this pack and the bytes that suppose to be data.
	data = struct.pack('!HH'+str(len(bytestosend))+'s', TFTP_OPCODES['data'], pack, bytestosend)
	r = random.randint(0,5)
	if r==0:
		print("--> Sending to client: PACK",pack,"(Retarded)")
		time.sleep(5.0)
		sock.sendto(data, client)
	else:
		if r!=1:
			print("--> Sending to client: PACK",pack)
			time.sleep(1.5)
			sock.sendto(data, client)
		else:
			print("--> Sending to client: PACK",pack, "(Lost)")
def send_ack(number, sock, client):							#This method is used to send an ack pack with the number of the pack that we want from the client.
	ack_msg = struct.pack('!HH', TFTP_OPCODES['ack'], number)
	print("--> Sending to client: ACK",number)
	time.sleep(1.0)
	sock.sendto(ack_msg, client)

def send_error(code, sock, client):							#This method is used to send an error with the number of this error and its description.
	error_string = server_error_msg[code]
	error_msg = struct.pack('!HH'+str(len(error_string))+'sB', TFTP_OPCODES['error'], code, error_string.encode(), 0)
	time.sleep(1.0)
	print("--> Sending to client: ERROR",code," ("+server_error_msg[code]+")")
	sock.sendto(error_msg, client)

def read_request(filename, client, sock):				#Used to do a read request
	path_name = "/home/raulbs/Documentos/"+filename
	if os.path.isfile(path_name):
		size = os.path.getsize (path_name) 
		num_packs = math.ceil(size/512)
		pack = 1
		f=open(path_name,'rb')
		bytestosend = f.read(512)

		while 1:
			try:					
				send_data_pack(bytestosend, pack, sock, client)						#We send a data pack.	
				msg, client = sock.recvfrom(4)
			except socket.error:										#If we haven't any response in a determinated time, we send another time the same packet.
				continue
			else:
				op = struct.unpack("!H", msg[0:2])[0]
				if op == 4:
					packReceived = struct.unpack("!H", msg[2:4])[0]
					print("<-- Receiving from client: ACK", packReceived)
					if packReceived == pack:						#If the number of pack received is equal to the next packet we have to send then we read from the file the data we need.
						if num_packs == pack:
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
		send_error(1, sock, client)											#If the file exists in the server we send an error because we can write in an existing file.

def write_request(filename, client, sock):									#Used to do a write requests
	path_name = "/home/raulbs/Documentos/"+filename
	if os.path.isfile(path_name):
		send_error(6, sock, client)											#If the file exists in the server we send an error because we can write in an existing file.
	else:
		f=open(path_name,'wb')
		pack = 0
		while 1:
			try:
				send_ack(pack, sock, client)									#We send an ack and we wait for receiving a data pack
				msg, client = sock.recvfrom(1024)
				
			except socket.error:
				continue
			else:
				op = struct.unpack("!H", msg[0:2])[0]
			 
				if op == 3:
					packReceived = struct.unpack("!H", msg[2:4])[0]
					print("<-- Receiving from client: PACK", packReceived)
					if packReceived == pack + 1:										#If the number of received pack is equal to the number of sequence of
						pack += 1													#good packets received then we write the data of this packet in the file.
						size = len(msg)
						dataLen = size - 4
						data = struct.unpack("!"+str(dataLen)+"s", msg[4:size])[0]
						f.write(data)
						if len(data) < 512:
							send_ack(pack,sock,client)
							return
				elif op == 2:
					continue
				else:
					print("There was an error in the receiving packets\n")
					break
	
if __name__== "__main__":
  main()
