import random
import socket
import json
from time import sleep

#Global Variables
clientID = '-1'
balance = 0
betPlace = False
cardTotal = 0
gameID = -1

#Functions:
#sendJson
#loginRequest
#joinQueue
#gamePacketHandler
#controlPacketHandler
#readJson
#clientLogic

#sendJson
#Input:Socket,Dictionary
#Outcome:Encodes and sends JSON
def sendJson(sock,jsonDict):
	print("SENDING:",jsonDict)
	sock.send(jsonDict)

#loginRequest
#Expected outcome: Sends login request to server
def loginRequest(sock):
	username = input("Username:")
	password = input("Password:")
	loginDetails = {
		"Username" : username,
		"Password" : password
	}
	jsonLogin = json.dumps(loginDetails).encode()
	sendJons(sock,jsonDict)

#joinQueue
#Expected outcome: Sends queue request to server
def joinQueue(sock):
	qType = input("Queue type: Test,Tournament")
	while not (qType == "Test" or qType == "Tournament"):
		print("ERROR: Invalid response")
		qtype = input("Select Test or Tournament")
	qDict = {
		"Queue" : qType
	}
	jsonQueue = json.dumps(qDict).encode()
	sendJson(sock,jsonQueue)

#clientLogic
#Expected outcome:Return Json containing whether or not we wanta nother card or not

def clientLogic(cardID):
	global cardTotal
	#Read the cardID(String)
	#update card total
	#return dictionary with HIT:True/False,player_id,game_id
	value = cardID[0]
	if value == 'J' or value == 'Q' or value == 'K':
		cardTotal += 10 
	if value == '9':
		cardTotal += 9
	if value == '8':
		cardTotal += 8
	if value == '7':
		cardTotal += 7
	if value == '6':
		cardTotal += 6
	if value == '5':
		cardTotal += 5
	if value == '4':
		cardTotal += 4
	if value == '3':
		cardTotal += 3
	if value == '2':
		cardTotal += 2
	if value == '1':
		if cardID[1] == '0':
			cardTotal += 10
		else:
			cardTotal += 1
	if cardTotal < 17:
		temp = {
			"packet_type" : "GAME",
			"game_id" : gameID,
			"player_id" : clientID,
			"MOVE" : "HIT",
			#TESTING - PLACEHOLDER
			#"BETAMT" : 10,
			"CONTROL": False
		}
	else:
			temp = {
			"packet_type" : "GAME",
			"game_id" : gameID,
			"player_id" : clientID,
			"MOVE" : "STAND",
			#TESTING - PLACEHOLDER
			#"BETAMT" : 10
		}
	return temp
		
#gamePacketHandler
#Expected outcome:Reads game JSON and updates values accordingly and sends corresponding packets
def gameJsonHandler(jsonDict,sock):
	global gameID
	global cardTotal
	if jsonDict["type"] == "RESET":
		if jsonDict["game_id"] == gameID:
			cardTotal = 0
	elif jsonDict["player_id"] == clientID:
		if gameID == -1:
			gameID = jsonDict["game_id"]
		if not gameID == jsonDict["game_id"]:
			print("ERROR: Received packet from wrong game - " , jsonDict["game_id"])
			print("Has correct playerID information,ERROR:Probably server side")
		else:
			cardID = jsonDict["card"]
			clientLogic(cardID)
			print("CARD TOTAL: ",cardTotal)
			print("HIT")
			#if  not cardTotal > 21:
				#sendJson(sock,hitJson)
				
	else:
		#1.Print out other player's moves
		#This is optional can do it later
		if gameID == -1:
			return 0
		if not gameID == jsonDict["game_id"]:
			#Error received packet from someone elses game
			print("ERROR: Received packet from wrong game - " + jsonDict["game_id"])

	

#Discuss Integration with ConnMan at a later date
#controlJsonHandler
def controlJsonHandler(jsonDict,sock):
	global clientID
	global cardTotal
	#print(jsonDict["subtype"])
	if clientID == '-1':
		print("SETUP ID")
		if jsonDict["subtype"] == "C":
			clientID = jsonDict["player_id"]
			print("CLIENTID: " , clientID)
			#joinQueue(sock)
	#TODO: Acknowledgement for correct player id
	elif jsonDict["player_id"] == clientID:
		if "type" in jsonDict:
			if jsonDict["type"] == "REQUEST":
				if jsonDict["item"] == "BETAMT":
					#print("BET 10")
					temp = {
						"packet_type" : "CONTROL",
						"BETAMT" : 10,
						"player_id" : clientID,
						"game_id": gameID
						}
					tempDump = json.dumps(temp).encode()
					sendJson(sock,tempDump)
					#print("POST BET")
				if jsonDict["item"] == "move":
					if cardTotal < 17:
						temp = {
							"packet_type" : "GAME",
							"MOVE" : "HIT",
							"player_id" : clientID,
							"game_id":gameID,
							"CONTROL": True
							}
						tempDump = json.dumps(temp).encode()
						sendJson(sock,tempDump)
						print("CARD TOTAL: ",cardTotal)
						print("HIT")
					else:
						temp = {
							"packet_type" : "GAME",
							"MOVE" : "STAND",
							"player_id" : clientID,
							"game_id":gameID
							}
						tempDump = json.dumps(temp).encode()
						sendJson(sock,tempDump)
						print("CARD TOTAL: ",cardTotal)
						print("STAND")
			

#readJson
#Expected outcome:Determines what type of json packet is and runs the appropriate function
def readJson(jsonDict,sock):
	#If this doesn't work use
	#json.loads(jsonDict)[0]
	print("NEW JSON : ",jsonDict)
	if jsonDict["packet_type"] == "CONTROL":
		controlJsonHandler(jsonDict,sock)
	elif jsonDict["packet_type"] == "GAME":
		gameJsonHandler(jsonDict,sock)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 3001)
print ('connecting to %s port %s' % server_address)
sock.connect(server_address)

#loginRequest(sock)
#joinQueue(sock)

#Socket Loop
try:
	while True:    
		exit = False
		# Loop for packet reading
		message = sock.recv(1024)
		amount_received = 0
		amount_expected = len(message)

		while amount_received < amount_expected:
			#data = sock.recv(1024)
			amount_received += len(message)
			packet = message.decode()
			print("PRE JSON LOADS(PACKET): " , packet)
			packetCount = packet.count("{")
			if(packetCount > 1):
				packetSplit = packet.split("}",packetCount - 1)
				for temp in packetSplit:
					load = temp + '}'
					#print("LOAD: ",load)
					packetJson = json.loads(load)
					print("POST JSON LOADS(PACKET): ", load)
					readJson(packetJson,sock)
			else:
				packetJson = json.loads(packet)
				print("POST JSON LOADS(PACKET): ", packetJson)
				readJson(packetJson,sock)				
		if exit:
			print("Exit is true\n")
			break
finally:    
	print ('closing socket')
	sock.close()
