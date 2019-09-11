#connection manager, written by Aidan Haile, 22234851
import socket
import threading
import queue
import json

#TODO add socket timeouts and unspecified socket family (ipv4 or ipv6)
#TODO add support to accept REST connections

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

	def start(self):
		super()
		print("in ListenServer.start")
		self.listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#hostname = socket.getHostName()
		hostname = ''
		port = 50519

		self.listenSocket.bind((hostname, port))
		self.listenSocket.listen(128)
		self.run()

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
	print("disconneting client " + client + " from server")
	notify = {"type" : "CONTROL", "subtype" : "DC"}
	send_message(addr, notify) #kind of a hack, requires client to dc first
	clientDict.pop(client)

#used by ConnMan to tell the game server a client disconnected from the server
#SHOULD NEVER BE CALLED BY THE GAME SERVER
def client_disconnected(addr):
	print("client " + addr + " has disconnected from server")
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