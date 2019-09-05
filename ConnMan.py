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
	if packet.length() == 0:
		raise SocketClosedException()

	if packet[0] != '{':
		raise IncorrectPacketFormatException()

	mess += packet

	depth = 1
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

class ConnMan:

	def __init__(self):
		self.clientDict = dict()
		self.msgQueue = queue.Queue()

	#starts the two threads for sending and receiving
	def start(self):
		threading.Thread(target=self.run_recv)
		#threading.Thread(target=self.runSend)

	#thread for sending messages down to the client
	"""
	def run_send(self):
		while True:
			while not msgQueue.empty():
				client, msg = queue.get()
				clientDict[client].sendall(msg)
	"""

	#thread for listening to the bound socket, and allocating threads to receive from clients
	#SHOULD NOT BE CALLED BY ANYTHING OTHER THAN CONNMAN
	def run_recv(self):
		while True:
			listenSocket = socket.socket(AF_INET, SOCK_STREAM)
			hostname = socket.getHostName()
			port = 5051

			listenSocket.bind((hostname, port))
			listenSocket.listen(128)

			addr, sock = listenSocket.accept()
			print("connection accepted from " + addr)

			self.clientDict[addr] = sock

			threading.Thread(target=self.handle_client, args=(addr, sock))


	#simply listens to the client connection and pushes it down to the game server
	def handle_client(self, addr, sock):
		client_is_connected = True
		while client_connected:
			try:
				message = recv_all(sock)
				print("message \"" + message + "\" from client " + addr)
				jdict = json.loads(message)
				if jdict.get("type") == "CONTROL":
					client_disconnected(client)
				messageTuple = (addr, jdict)
				self.msgQueue.put(messageTuple)

			except SocketClosedException:
				client_disconnected(addr)
				client_is_connected = False

			except IncorrectPacketFormatException:
				#in future, ask for resend
				client_disconnected(addr)
				client_is_connected = False


	#used for disconnecting a client from the game
	def disconnect_client(self, addr):
		print("disconneting client " + client + " from server")
		self.clientDict[client].close()
		self.clientDict.pop(client)

	#used by ConnMan to tell the game server a client disconnected from the server
	#SHOULD NEVER BE CALLED BY THE GAME SERVER
	def client_disconnected(self, addr):
		print("client " + addr + " has disconnected from server")
		disconnect_client(addr)
		dcNotify = (addr, { "type" : "CONTROL", "subtype" : "DC"})
		self.msgQueue.put(dcNotify)
		

	#sends a message down to the client over the connection
	def send_message(self, addr, message):
		print("sending message \"" + message + "\" to client " + addr)
		fm_msg = json.dumps(message)
		self.clientDict[addr].sendall(fm_msg)

	#fetches the top message from the message queue, or returns None if empty
	#returns a tuple with the form (address, dictionary) with the dictionary a formatted json response
	def get_message(self):
		if self.msgQueue.empty():
			return None
		else:
			return self.msgQueue.get()