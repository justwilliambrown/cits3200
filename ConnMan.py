#connection manager, written by Aidan Haile, 22234851
import socket
import threading
import queue
import json
import time
import matchmaking_Server
import werkzeug.security
import database

class SocketClosedException(Exception):
	pass

class IncorrectPacketFormatException(Exception):
	pass

#simply a helper function that receives an entire json object over the supplied socket
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
		if len(packet) == 0:
			raise SocketClosedException()

		depth += packet.count("{")
		depth -= packet.count("}")

		mess += packet

	if depth < 0:
		raise IncorrectPacketFormatException()

	return mess

#connman data structures
clientDict = dict()
gameMsgQueues = dict()
connectMsgQueue = queue.Queue()
clientGameIdentifier = dict()
#------------------------------------------------

#starts the two threads for sending and receiving
def start():
	x = threading.Thread(target=ListenServer)
	x.start()

#class that implements the socket for listening for conections
class ListenServer(threading.Thread):

	def __init__(self):
		super()
		self.start()

	def start(self):
		super()
		self.listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		hostname = ''
		port = 3001

		self.listenSocket.bind((hostname, port))
		self.listenSocket.listen(128)
		self.run()

	#thread for listening to the bound socket, and allocating threads to receive from clients
	#SHOULD NOT BE CALLED BY ANYTHING OTHER THAN CONNMAN
	def run(self):
		super()
		print("ListenServer initialised")
		while True:
			sock, addr = self.listenSocket.accept()
			print("connection accepted from ", addr)

			x = threading.Thread(target=ClientHandle, args=(addr, sock))
			x.start()
#---------------------------------------------------------------------------------------------

#class that implements listening for packets from the client and forwarding it to where it's needed
class ClientHandle(threading.Thread):
	def __init__(self, addr, sock):
		self.addr = addr
		self.sock = sock
		self.start()

	def start(self):
		if not self.authenticate():
			self.sock.sendall('{"packet_type" : "CONTROL", "subtype", "loginDeny"}'.encode())
			self.sock.close()
			return

		loginAcceptPacket = {"packet_type" : "CONTROL", "subtype" : "loginAccept", "id" : self.client_id}
		self.sock.sendall((json.dumps(loginAcceptPacket)).encode())
		clientDict[self.client_id] = self.sock

		connectionNotify = {"packet_type" : "CONTROL", "subtype" : "C","player_id" : self.client_id, "rank" : self.rank}
		connectMsgQueue.put(connectionNotify)
		self.run()

	#simply listens to the client connection and pushes it down to the game server
	def run(self):
		client_is_connected = True
		while client_is_connected:
			try:
				message = recv_all(self.sock)
				if clientDict.get(self.client_id) == None:
					self.sock.close() #making sure no bad acters ignore disconnect and cause havoc
					client_is_connected = False
					break

				#print("message \"" + message + "\" from client ", self.client_id)
				jdict = json.loads(message)
				if "subtype" in jdict.keys():
					client_disconnected(self.client_id)
					self.sock.close()

				#if jdict.get("player_id") != self.client_id and jdict.get("game_id") != clientGameIdentifier.get(self.client_id):
					#client_disconnected(self.client_id)
					#self.sock.close()
				if jdict.get("Queue") != None:
					connectMsgQueue.put(jdict)
				else:
					gameMsgQueues[jdict.get("game_id")].put(jdict)

			except SocketClosedException:
				print("socket connection was closed")
				client_disconnected(self.client_id)
				self.sock.close()
				client_is_connected = False
				break

			except IncorrectPacketFormatException:
				print("packet was formatted incorrectly")
				#in future, ask for resend
				client_disconnected(self.client_id)

				self.sock.close()
				client_is_connected = False
				break

	#authenticates the user, making sure they are allowed to join
	def authenticate(self):
		dbCursor = database.getDB().cursor(prepared=True)
		stmt = "SELECT id, username, password_hash, ranking FROM user WHERE username = %s"
		
		loginReq = '{"packet_type" : "CONTROL", "subtype" : "loginRequest"}'
		self.sock.sendall(loginReq.encode())
		message = ''
		try:
			message = recv_all(self.sock)
		except SocketClosedException:
			dbCursor.close()
			return False

		jdict = json.loads(message)
		
		dbCursor.execute(stmt, (jdict["user"],))

		for (ID, username, pHash, rank) in dbCursor:
			if werkzeug.security.check_password_hash(pHash, jdict["pass"]):
				self.client_id = ID;
				if ID in clientDict.keys():
					return False
				self.rank = rank
				dbCursor.close()
				return True
		dbCursor.close()
		return False
#----------------------------------------------------------------------------

#used for disconnecting a client from the game
def disconnect_client(addr):
	if addr not in clientDict:
		return None
	print("disconneting client {0} from server".format(addr))
	notify = {"packet_type" : "CONTROL", "subtype" : "DC", "player_id" : addr}
	send_message(addr, notify) #kind of a hack, requires client to dc first
	matchmaking_Server.playerDisconnect(addr)
	tempsock = clientDict.get(addr)
	clientDict.pop(addr)
	tempsock.close()


#used by ConnMan to tell the game server a client disconnected from the server
#SHOULD NEVER BE CALLED BY THE GAME SERVER
def client_disconnected(addr):
	print("client {0} has disconnected from server".format(addr))
	if addr in clientDict:
		clientDict.pop(addr)
	
	dcNotify = { "packet_type" : "CONTROL", "subtype" : "DC", "player_id" : addr}
	
	if addr in clientGameIdentifier:
		gameMsgQueues.get(clientGameIdentifier.get(addr)).put(dcNotify)
	#connectMsgQueue.put(dcNotify)
	matchmaking_Server.playerDisconnect(addr)


#sends a message down to the client over the connection
def send_message(addr, message):
	#print("sending message \"{0}\" to client {1}".format(message, addr))
	fm_msg = json.dumps(message).encode()

	try:
		if message.get("type") == "BROADCAST":
			game = message.get("game_id")
			for clients in clientGameIdentifier.items():
				if clients[1] == game:
					try:
						clientDict[clients[0]].sendall(fm_msg)
					except Exception:
						continue; #just make sure it continues even if there's a socket error
		else:
			clientDict[addr].sendall(fm_msg)
	except KeyError:
		return #client has been disconnected/has disconnected. Simply ignore this send to avoid a crash

#fetches the top message from the message queue, or returns None if empty
#returns a tuple with the form (client id, dictionary) with the dictionary a formatted json response
def get_game_message(game_id, blocking=False):
	try:
		temp = gameMsgQueues[game_id].get(block=blocking)
		return temp
		#return gameMsgQueues[game_id].get(block=blocking)
	except queue.Empty:

		return None

def get_match_message(blocking=False):
	try:
		return connectMsgQueue.get(block=blocking)
	except queue.Empty:

		return None

def start_game(game_id, clientList):
	for client in clientList:
		clientGameIdentifier[client] = game_id
	gameMsgQueues[game_id] = queue.Queue()

def end_game(game_id, clientList):
	for client in clientList:
		clientGameIdentifier.pop(client)
	gameMsgQueues.pop(game_id)
