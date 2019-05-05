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
import random

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

def main():

	initialization_handler()
	destination = argv[2]
	port = int(argv[4])
	sock = socket(AF_INET, SOCK_STREAM)
	sock.connect((destination, port))

	while 1:
	
		command = input('TFTP@TCP> ')

		if not command: break
	
		order(command, sock)

	sock.close()

def initialization_handler():			#This method controls that the arguments we pass in the command
	if len(argv) != 5:					#line is correct or not. 
		print(__doc__ % argv[0])
		exit(1)
	if argv[1].lower() != "-s":
		print(__doc__ % argv[0])
		exit(1)
	if argv[3].lower() != "-p":
		print(__doc__ % argv[0])
		exit(1)	

def order(command, sock):									#This method is used to the handling of the requests made by the client.
	sending = command.split()
	if sending[0].lower() == "read":
		if len(sending) == 1: exit(1)
		fileName = sending[1]
		receive_data(fileName, sock)

	elif sending[0].lower() == "write":
		if len(sending) == 1: exit(1)
		fileName = sending[1]
		send_data(fileName, sock)
	elif sending[0].lower() == "quit":
		exit(1)
	else:
		print("""\
The operation introduced is not correct. The available operations are:
	- read <file>
	- write <file>
	- quit
		""")

def send_write_request(filename, sock):			#This method is used to send a message of a write request.
	data = struct.pack('!H'+str(len(filename))+'sB'+str(len(modes[0]))+'sB', TFTP_OPCODES['write'], filename.encode(), 0,modes[0].encode(), 0)
		# ends with ''
	print("--> Sending to server: WRQ of file '"+filename+"'")
	sock.send(data)

def send_read_request(filename, sock):			#This method is used to send a message of a read request.
	data = struct.pack('!H'+str(len(filename))+'sB'+str(len(modes[0]))+'sB', TFTP_OPCODES['read'], filename.encode(), 0,modes[0].encode(), 0)
		# ends with ''
	print("--> Sending to server: RRQ of file '"+filename+"'")
	sock.send(data)

def send_data_pack(bytestosend, pack, sock):		#This method is used to send a data pack with the number of this pack and the bytes that suppose to be data.
	data = struct.pack('!HH'+str(len(bytestosend))+'s', TFTP_OPCODES['data'], pack, bytestosend)
	print("--> Sending to server: PACK",pack)
	time.sleep(1.5)
	sock.send(data)

def error_server(msg):						#This method is used to decodificate the information of an error message proceding of the server.
	error_code = struct.unpack("!H", msg[2:4])[0]
	error_string_end = msg.find(0, 4)
	error_string_len = error_string_end - 4
	error_string = struct.unpack("!"+str(error_string_len)+"s", msg[4:error_string_end])[0].decode()
	print('Error',error_code,':',error_string)

def receive_data(filename, sock):					#This method is in charge of receiving data when you send a read request.
	path_name = "/home/raulbs/Descargas/"+filename
	if os.path.isfile(path_name):						#If we have a file with this name we throw an error.
		print('Error',6,':',server_error_msg[6])
	else:
		begin_time = time.time()							#Pack variable indicates the number of not repeated pack received from the server.
		send_read_request(filename, sock)
		pack=1
		f=open(path_name,'wb')
		while 1:
			msg = sock.recv(516)
			op = struct.unpack("!H", msg[0:2])[0]
		
			if op == TFTP_OPCODES['data']:
				packReceived = struct.unpack("!H", msg[2:4])[0]
				print("<-- Receiving from server: PACK",packReceived)
				if pack == packReceived:							#If the number of received pack is equal to the number of sequence of
					pack += 1										#good packets received then we write the data of this packet in the file.
					size = len(msg)
					dataLen = size - 4
					data = struct.unpack("!"+str(dataLen)+"s", msg[4:size])[0]
					f.write(data)
					if len(data) < 512:
						break
			elif op == TFTP_OPCODES['error']:
				error_server(msg)
				break
			else:
				print("There was an error in the receiving packets\n")
				break
		execution_time = time.time() - begin_time
		print("------Reading time: %.10f seconds------" %execution_time)

def send_data(filename, sock):						#This method is in charge of sending data when you send a write request.
	path_name = "/home/raulbs/Descargas/"+filename
	if os.path.isfile(path_name):
		begin_time = time.time()
		send_write_request(filename, sock)
		size = os.path.getsize (path_name) 									#We obtain the size of the file.
		num_packs = math.ceil(size/512)										#Now we divide the size of this file in 512 bytes that it is the maximum
		pack = 0															#number of bytes that a data pack can carry. The value obtained rounded is the
		f=open(path_name,'rb')												#quantity of packets we need to send all the file.
		msg = sock.recv(1024)													#First we need to receive a message from the server, it can be an error or it can
		op = struct.unpack("!H", msg[0:2])[0]								#be an ack to confirm that it is possible to upload to the server this file because, for example,
		while 1:															#it doesn't exits other file with the same name.
			if op == TFTP_OPCODES['ack']:
				if num_packs == pack:										#If we have send yet all the packets corresponding of the file, it breaks the while.
					break
				else:
					bytestosend = f.read(512)
					pack += 1
					send_data_pack(bytestosend, pack, sock)			
			elif op == TFTP_OPCODES['error']:								#If we receive an error message, we want to know what happened and we exit the loop.
				error_server(msg)
				break
			else:
				print("There was an error in the receiving ACK\n")
				break
		execution_time = time.time() - begin_time
		print("------Writing time: %.10f seconds------" %execution_time)
	else:
		print('Error',1,':',server_error_msg[1])							#If we haven't a file with this name we throw an error.

if __name__== "__main__":
  main()
