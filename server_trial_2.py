#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
from socket import *
from pickle import *
from sys import *
from struct import *
import time

def handle(sock, msg, client, n):
	print('New request', n, client)
	real_msg = unpack('=2h',msg)
	print('Type: ', real_msg)
	time.sleep(1)
	sock.sendto(msg,client)

if len(argv) != 2:
	print(__doc__ % argv[0])
	exit(1)

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(('', int(argv[1])))

n = 0
while 1:
	msg, client = sock.recvfrom(1024)
	n += 1
	handle(sock, msg, client, n)
