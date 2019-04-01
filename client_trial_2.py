"Usage: %s -S <server> -P <port>"
from socket import *
from pickle import *
from sys import *
import struct


def initialization_handler():
	if len(argv) != 5:
		print(__doc__ % argv[0])
		exit(1)
	if argv[1].lower() != "-s":
		print(__doc__ % argv[0])
		exit(1)
	if argv[3].lower() != "-p":
		print(__doc__ % argv[0])
		exit(1)	

def analyze(command):
	args = command.split()
	if args[0].lower() == "read":
		if len(args) == 1: exit(1)
		fileName = args[1].encode()
		mode = b'NETASCII'
		data = struct.pack('!H'+str(len(fileName))+'sB'+str(len(mode))+'sB', 1, fileName, 0,mode, 0)
		# ends with ''
		sock.sendto(data, (destination, port))
	elif args[0].lower() == "write":
		fileName = args[1].encode()
		mode = b'NETASCII'
		data = struct.pack('!H'+str(len(fileName))+'sB'+str(len(mode))+'sB', 2, fileName, 0,mode, 0)
		# ends with ''
		sock.sendto(data, (destination, port))
	elif args[0].lower() == "quit":
		exit(1)
	else:
		print("""\
The operation introduced is not correct. The available operations are:
	- read <file>
	- write <file>
	- quit
		""")

initialization_handler()
destination = argv[2]
port = int(argv[4])
sock = socket(AF_INET, SOCK_DGRAM)

while 1:
	
	command = input('TFTP@UDP> ')

	if not command: break
	analyze(command)
	msg, server = sock.recvfrom(1024)
	print(struct.unpack('!6s', msg))

sock.close()
