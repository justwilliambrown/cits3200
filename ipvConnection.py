## testing Connection manager for socket connection for both ipv4 and ipv6
## from line 56
import socket
import threading
import queue
import json
import sys

class SocketClosedException(Exception):
	pass

class IncorrectPacketFormatException(Exception):
	pass

def recv_all(sock):
	mess = ''
	packet = sock.recv(1024).decode()
	if len(packet) == 0:
		raise SocketClosedException()

	if packet[0] != '{':
		raise IncorrectPacketFormatException()

	mess += packet

	depth = packet.count('{') - packet.count('}')
	while depth > 0:
		packet = sock.recv(1024).decode()
		if packet.length() == 0:
			raise SocketClosedException()

		depth += packet.count("{")
		depth -= packet.count("}")

		mess += packet

	if depth < 0:
		raise IncorrectPacketFormatException()

	return mess

clientDict = dict()
msgQueue = queue.Queue()

#starts the two threads for sending and receiving
def start():
	x = threading.Thread(target=ListenServer)
	x.start()

class ListenServer(threading.Thread):

	def __init__(self):
		super()
		print("listen server initialised")
		self.start()

    #  using getaddrinfo to inspect the connection then connect respectively
	def start(self):
		super()
		print("in ListenServer.start")
        hostname = ''
		port = 50519

        info = socket.getaddrinfo(hostname, port, proto=socket.IPPROTO_TCP)
        
        for each in info:
            #  accesssing the first three elements (family, sock-type, proto) 
            try: 
                self.listenSocket = socket.socket(*each[0:3])
            except OSError as msg:
                self.listenSocket = None
                continue
            try:
                self.listenSocket.bind(each[4])
                self.listenSocket.listen(128)
		        self.run()
            except OSError as msg :
                self.listenSocket.close()
                self.listenSocket = None
                continue

	#thread for listening to the bound socket, and allocating threads to receive from clients
	#SHOULD NOT BE CALLED BY ANYTHING OTHER THAN CONNMAN
	def run(self):
		super()
		print("in ListenServer.run")
		while True:
			sock, addr = self.listenSocket.accept()
			print("connection accepted from ", addr)

			clientDict[addr] = sock

			x = threading.Thread(target=ClientHandle, args=(addr, sock))
			x.start()

class ClientHandle(threading.Thread):
	def __init__(self, addr, sock):
		self.addr = addr
		self.sock = sock
		self.start()

	def start(self):
		self.run()

	#simply listens to the client connection and pushes it down to the game server
	def run(self):
		client_is_connected = True
		while client_is_connected:
			try:
				message = recv_all(self.sock)
				if clientDict.get(self.addr) == None:
					self.sock.close() #making sure no bad acters ignore disconnect and cause havoc
					client_is_connected = False
					break

				print("message \"" + message + "\" from client ", self.addr)
				jdict = json.loads(message)
				if jdict.get("type") == "CONTROL":
					client_disconnected(client)
				messageTuple = (self.addr, jdict)
				msgQueue.put(messageTuple)

			except SocketClosedException:
				print("socket connection was closed")
				client_disconnected(self.addr)
				self.sock.close()
				client_is_connected = False
				break

			except IncorrectPacketFormatException:
				print("packet was formatted incorrectly")
				#in future, ask for resend
				client_disconnected(self.addr)
				self.sock.close()
				client_is_connected = False
				break


#used for disconnecting a client from the game
def disconnect_client(addr):
	print("disconneting client {0} from server", addr)
	notify = {"type" : "CONTROL", "subtype" : "DC"}
	send_message(addr, notify) #kind of a hack, requires client to dc first
	clientDict.pop(client)

#used by ConnMan to tell the game server a client disconnected from the server
#SHOULD NEVER BE CALLED BY THE GAME SERVER
def client_disconnected(addr):
	print("client {0} has disconnected from server", )
	disconnect_client(addr)
	dcNotify = (addr, { "type" : "CONTROL", "subtype" : "DC"})
	msgQueue.put(dcNotify)
	

#sends a message down to the client over the connection
def send_message(addr, message):
	print("sending message \"{0}\" to client {1}", message, addr)
	fm_msg = json.dumps(message).encode()
	clientDict[addr].sendall(fm_msg)

#fetches the top message from the message queue, or returns None if empty
#returns a tuple with the form (address, dictionary) with the dictionary a formatted json response
def get_message():
	if msgQueue.empty():
		return None
	else:
		return msgQueue.get()