#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
"usage: <port>"
"UDP server"

from socket import *
from pickle import *
from sys import *
import time
from socketserver import *


def handle(sock, msg, client, n):
	print('New request', n, client)
	time.sleep(1) # some job
	sock.sendto(msg.upper(),client)

if len(argv) != 2:
	print(__doc__ % argv[0])
	exit(1)
	
def main():
	sock = socket(AF_INET, SOCK_DGRAM)
	sock.bind(('', int(argv[1])))

n = 0
while 1:
	msg, client = sock.recvfrom(1024)
	n += 1
	handle(sock, msg, client, n)

if __name__ == '__main__':
   try:
       sys.exit(main())
   except KeyboardInterrupt:
       pass
