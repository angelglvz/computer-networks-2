#!/usr/bin/python
"Usage: %s <port>"
from socket import *
from sys import *
import struct
import time
import os
import math
import _thread,time

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
	sock=socket(AF_INET,SOCK_STREAM)
	sock.bind(('',port))
	sock.listen(5)
	n = 0

	while 1:
		child_sock, client = sock.accept()
		n += 1
		_thread.start_new_thread(handle, (child_sock, client, n))

def initialization_handler():					#This method controls that the arguments we pass in the command
	if len(argv)!= 3:							#line is correct or not.
		print(__doc__ % argv[0])
		exit(1)
	if argv[1].lower() != "-p":
		print(__doc__ % argv[0])
		exit(1)

def request_handler(sock, msg, client, n):		#This method is used to the handling of the requests sent by the client.
	print('  New request:', n, "from",client)
	op = struct.unpack("!H", msg[0:2])[0]

	if op == 1:
		filenameEnd = msg.find(0, 2)
		filenameLen = filenameEnd - 2
		filename = struct.unpack("!"+str(filenameLen)+"s", msg[2:filenameEnd])[0].decode()
		modeEnd = msg.find(0, filenameEnd+1)
		modeLen = modeEnd - (filenameEnd + 1)
		mode = struct.unpack("!"+str(modeLen)+"s", msg[filenameEnd+1:modeEnd])[0].decode()
		read_request(filename, sock, client)
	elif op == 2:
		filenameEnd = msg.find(0, 2)
		filenameLen = filenameEnd - 2
		filename = struct.unpack("!"+str(filenameLen)+"s", msg[2:filenameEnd])[0].decode()
		modeEnd = msg.find(0, filenameEnd+1)
		modeLen = modeEnd - (filenameEnd + 1)
		mode = struct.unpack("!"+str(modeLen)+"s", msg[filenameEnd+1:modeEnd])[0].decode()
		write_request(filename, sock, client)
	else:
		print("There is an error in the request of the client.")

def send_data_pack(bytestosend, pack, sock, client):		#This method is used to send a data pack with the number of this pack and the bytes that suppose to be data.
	data = struct.pack('!HH'+str(len(bytestosend))+'s', 3, pack, bytestosend)
	time.sleep(1.5)
	print("  --> Sending to client "+str(client)+": PACK",pack)
	sock.send(data)
def send_error(code, sock, client):							#This method is used to send an error with the number of this error and its description.
	error_string = server_error_msg[code]
	error_msg = struct.pack('!HH'+str(len(error_string))+'sB', 5, code, error_string.encode(), 0)
	time.sleep(1.0)
	print("  --> Sending to client "+str(client)+ ": ERROR",code," ("+server_error_msg[code]+")")
	sock.send(error_msg)
def send_ack(number, sock, client):							#This method is used to send an ack pack that is only used who time.
	ack_msg = struct.pack('!HH', TFTP_OPCODES['ack'], number)
	print("  --> Sending to client "+str(client)+": ACK",number)
	time.sleep(0.5)
	sock.send(ack_msg)

def read_request(filename, sock, client):					#Used to perform a read request
	path_name = "/home/raulbs/Documentos/"+filename
	if os.path.isfile(path_name):
		size = os.path.getsize (path_name) 
		num_packs = math.ceil(size/512)
		pack = 0
		f=open(path_name,'rb')

		while 1:
			if num_packs == pack:
				break
			else:
				bytestosend = f.read(512)
				send_data_pack(bytestosend, pack, sock, client)
				pack += 1
	else:										
		send_error(1, sock, client)								#If the file doesn't exist in the server we send an error because we can't read this file.

def write_request(filename, sock, client):						#Used to do a write request
	path_name = "/home/raulbs/Documentos/"+filename
	if os.path.isfile(path_name):						#If the file exists in the server we send an error because we can write in an existing file.
		send_error(6, sock, client)
	else:
		f=open(path_name,'wb')
		pack = 0
		send_ack(pack, sock, client)							#First we send an ack to tell the client it is possible to send to the server this file.
		while 1:
			msg = sock.recv(516)

			if msg:

				op = struct.unpack("!H", msg[0:2])[0]
			 
				if op == 3:
					packReceived = struct.unpack("!H", msg[2:4])[0]
					print("  <-- Receiving from client "+str(client)+": PACK", packReceived)
					if pack == packReceived:									#If the number of received pack is equal to the number of sequence of
						pack += 1												#good packets received then we write the data of this packet in the file.
						size = len(msg)
						dataLen = size - 4
						data = struct.unpack("!"+str(dataLen)+"s", msg[4:size])[0]
						f.write(data)
						if len(data) < 512:
							return
				elif op == 2:
					continue
				else:
					print("There was an error in the receiving packets\n")
					break

def handle(sock, client,n):									#Method to handle the connection of one client to the server
	print('Client connected:',n,client)
	num = 0
	while 1:
		msg = sock.recv(1024)
		num += 1
		request_handler(sock, msg, client, n)
	sock.close()

if __name__== "__main__":
  main()
