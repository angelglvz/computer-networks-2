#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
from socket import *
import sys
import pickle

def main():
	

	f=open('ListinLlamadas','r')
	
	sock = socket(AF_INET, SOCK_DGRAM)

	while True:
		
		msg=f.read(12)
		
		sock.sendto(msg,('',12345))
		sock.close()

if __name__ == '__main__':
	try:
		sys.exit(main())
	except KeyboardInterrupt:
		pass
