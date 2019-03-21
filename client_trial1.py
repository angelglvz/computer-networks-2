#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
from socket import *
from pickle import *
from sys import *


def sending():
	while 1:
		
def main():
    f=open('ListinLlamadas','rb')

    while True:
        msg= f.read(12)

        print(struct.unpack('=2B2IH',msg))

        sock = socket(AF_INET, SOCK_DGRAM)

        sock.sendto(msg, ('', 12345))
        sock.close()

        if not msg: break

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass

