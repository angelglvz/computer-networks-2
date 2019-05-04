#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"Usage: %s -S <server> -P <port>"
import socket
from pickle import *
from sys import *
import struct
import math
import os
from time import time
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
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sec = 4																					#Timeout of four seconds
	usec = 10000
	timevalue = struct.pack('ll', sec, usec)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timevalue)

	while 1:
	
		command = input('TFTP@UDP> ')												#We input an order

		if not command: break
	
		order(command,sock,destination,port)
	

	sock.close()

def initialization_handler():						#This method controls that the arguments we pass in the command
	if len(argv) != 5:								#line is correct or not.
		print(__doc__ % argv[0])
		exit(1)
	if argv[1].lower() != "-s":
		print(__doc__ % argv[0])
		exit(1)
	if argv[3].lower() != "-p":
		print(__doc__ % argv[0])
		exit(1)	

def order(command,sock,destination,port):				#This method is used to the handling of the requests made by the client
	sending = command.split()
	if sending[0].lower() == "read":
		if len(sending) == 1: exit(1)
		fileName = sending[1]
		
		receive_data(fileName,sock,destination,port)

	elif sending[0].lower() == "write":
		if len(sending) == 1: exit(1)
		fileName = sending[1]
		send_data(fileName,sock,destination,port)
	elif sending[0].lower() == "quit":
		exit(1)
	else:
		print("""\
The operation introduced is not correct. The available operations are:
	- read <file>
	- write <file>
	- quit
		""")


def send_write_request(filename,sock,destination,port):			#This method is used to send a message of a write request.
	data = struct.pack('!H'+str(len(filename))+'sB'+str(len(modes[0]))+'sB', TFTP_OPCODES['write'], filename.encode(), 0,modes[0].encode(), 0)
		# ends with ''
	print("--> Sending to server: WRQ of file '"+filename+"'")
	sock.sendto(data, (destination, port))

def send_read_request(filename,sock,destination,port):			#This method is used to send a message of a read request.
	data = struct.pack('!H'+str(len(filename))+'sB'+str(len(modes[0]))+'sB', TFTP_OPCODES['read'], filename.encode(), 0,modes[0].encode(), 0)
		# ends with ''
	print("--> Sending to server: RRQ of file '"+filename+"'")
	sock.sendto(data, (destination, port))

def send_data_pack(bytestosend, pack, sock, destination, port):	#This method is used to send a data pack with the number of this pack and the bytes that suppose to be data.
	data = struct.pack('!HH'+str(len(bytestosend))+'s', TFTP_OPCODES['data'], pack, bytestosend)
	print("--> Sending to server: PACK",pack)
	sock.sendto(data, (destination,port))

def send_ack(number,sock,destination,port):						#This method is used to send an ack pack with the number of the pack that we want from the client.
	ack_msg = struct.pack('!HH', TFTP_OPCODES['ack'], number)
	print("--> Sending to server: ACK",number)
	sock.sendto(ack_msg, (destination,port))

def error_server(msg):							#This method is used to decodificate the information of an error message proceding of the server.
	error_code = struct.unpack("!H", msg[2:4])[0]
	error_string_end = msg.find(0, 4)
	error_string_len = error_string_end - 4
	error_string = struct.unpack("!"+str(error_string_len)+"s", msg[4:error_string_end])[0].decode()
	print('Error ',error_code,': ',error_string)

def send_data(filename,sock,destination,port):					#This method is in charge of sending data when you send a write request.
	path_name = "/home/raulbs/Descargas/"+filename
	if os.path.isfile(path_name):
		begin_time = time()
		send_write_request(filename,sock,destination,port)
		size = os.path.getsize (path_name) 
		num_packs = math.ceil(size/512)
		pack = 0
		f=open(path_name,'rb')
	
		try:												#First of all we expect the first ack pack.
			msg, server = sock.recvfrom(1024)

		except socket.error:
			send_write_request(filename,sock,destination,port)				#If we don't receive the first ack pack, we send another time the write request.
		else:
			op = struct.unpack("!H", msg[0:2])[0]
			if op == 4:													#If we receive the first ack pack, we send the first data pack to the server				
				packReceived = struct.unpack("!H", msg[2:4])[0]			#and we increment the number of different data packs sent.
				print("<-- Receiving from server: ACK", packReceived)
				bytestosend = f.read(512)
				send_data_pack(bytestosend, packReceived,sock,destination,port)
				pack += 1
			elif op == 5:
				error_server(msg)
				return 
			else:
				print("There was an error in the receiving ACK\n")
				return

		while 1:
			try:
				msg, server = sock.recvfrom(1024)

			except socket.error:									#If we don't receive any ack pack we have two posibilities: if we doesn't receive the first ack pack
				if pack == 0:										#we send another time the write request and if not, we send the same data pack we have sent before.
					send_write_request(filename,sock,destination,port)
				else:
					send_data_pack(bytestosend, packReceived,sock,destination,port)
			else:
				op = struct.unpack("!H", msg[0:2])[0]
				if op == 4:
					packReceived = struct.unpack("!H", msg[2:4])[0]
					print("<-- Receiving from server: ACK", packReceived)	
					if packReceived == pack:								#If we have send yet all the packets corresponding of the file, it breaks the while. If not we send
						if num_packs == pack:								#the next data pack. If it is an ack repeated we send another time the same data pack we send before.
							break
						else:
							bytestosend = f.read(512)
							send_data_pack(bytestosend, packReceived,sock,destination,port)
							pack += 1
					else:
						send_data_pack(bytestosend, packReceived,sock,destination,port)
				elif op == 5:
					error_server(msg)
					break
				else:
					print("There was an error in the receiving ACK\n")
					break

		execution_time = time() - begin_time
		print("------Reading time: %.10f seconds------" %execution_time)
	else:
		print('Error',1,':',server_error_msg[1])

def receive_data(filename, sock, destination, port):						#This method is in charge of receiving data when you send a read request.
	path_name = "/home/raulbs/Descargas/"+filename
	if os.path.isfile(path_name):
		print('Error',6,':',server_error_msg[6])
	else:
		begin_time = time()
		send_read_request(filename,sock,destination,port)
		pack = 0
		f=open(path_name,'wb')
		try:
			msg, server = sock.recvfrom(1024)						#First of all we expect the first data pack.
		except socket.error:
			send_read_request(filename,sock,destination,port)		#If we don't receive the first data pack, we send another time the read request.
		else:
			op = struct.unpack("!H", msg[0:2])[0]
			
			if op == 3:
				packReceived = struct.unpack("!H", msg[2:4])[0]						#If we receive the first data pack, we send the first ack pack to the server				
				print("<-- Receiving from server: PACK", packReceived)					#and we increment the number of different data packs received.	
				if pack == packReceived:
					pack += 1
					size = len(msg)
					dataLen = size - 4
					data = struct.unpack("!"+str(dataLen)+"s", msg[4:size])[0]
					f.write(data)			
					if len(data) < 512:
						execution_time = time() - begin_time
						print("------Reading time: %.10f seconds-----" %execution_time)
						send_ack(pack,sock,destination,port)
						return
					else:
						send_ack(pack,sock,destination,port)
			elif op == 5:
				error_server(msg)
				return
			else:
				print("There was an error in the receiving packets\n")
				return

		while 1:
			try:
				msg, server = sock.recvfrom(1024)
			except socket.error:													#If we don't receive any data pack we have two posibilities: if we doesn't receive the first data pack
				if pack == 0:														#we send another time the read request and if not, we send the same ack pack we have sent before.
					send_read_request(filename,sock,destination,port)
				else:
					send_ack(pack,sock,destination,port)							
			else:
				op = struct.unpack("!H", msg[0:2])[0]
		
				if op == 3:
					packReceived = struct.unpack("!H", msg[2:4])[0]
					print("<-- Receiving from server: PACK", packReceived)				#If we have receive the last data pack, we send to the server the last data pack and we skip the loop. If not we send
					if pack == packReceived:										#the next ack pack. If it is a data pack repeated, we send the last ack pack we send before.
						pack += 1
						size = len(msg)
						dataLen = size - 4
						data = struct.unpack("!"+str(dataLen)+"s", msg[4:size])[0]
						f.write(data)			
						if len(data) < 512:
							send_ack(pack,sock,destination,port)
							break
						else:
							send_ack(pack,sock,destination,port)
				elif op == 5:
					error_server(msg)
					break
				else:
					print("There was an error in the receiving packets\n")
					break

		execution_time = time() - begin_time
		print("------Reading time: %.10f seconds-----" %execution_time)

if __name__== "__main__":
  main()
