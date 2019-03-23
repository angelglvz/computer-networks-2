#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
from socket import *
from pickle import *
from sys import *

def handle(sock, msg, client, n):
	print('New request', n, client)
	time.sleep(1) # some job
	sock.sendto(msg.upper(),client)

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
