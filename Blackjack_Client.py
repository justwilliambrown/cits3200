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
def sendJson(socket,jsonDict):
	jsonDict.encode()
	socket.send(jsonDict)

#loginRequest
#Expected outcome: Sends login request to server
def loginRequest(socket):
	username = input("Username:")
	password = input("Password:")
	loginDetails = {
		"Username" : username,
		"Password" : password
	}
	jsonLogin = json.dumps(loginDetails)
	sendJons(socket,jsonDict)

#joinQueue
#Expected outcome: Sends queue request to server
def joinQueue(socket):
	qType = input("Queue type: Test,Tournament")
	while not (qType == "Test" or qType == "Tournament"):
		print("ERROR: Invalid response")
		qtype = input("Select Test or Tournament")
	qDict = {
		"Queue" : qType
	}
	jsonQueue = json.dumps(qDict)
	sendJson(socket,jsonQueue)

#clientLogic
#Expected outcome:Return Json containing whether or not we wanta nother card or not

def clientLogic(cardID):
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
			"hit" : True
			#TESTING - PLACEHOLDER
			#"bet_amount" : 100
		}
	else:
			temp = {
			"packet_type" : "GAME",
			"game_id" : gameID,
			"player_id" : clientID,
			"hit" : False
			#TESTING - PLACEHOLDER
			#"bet_amount" : 100
		}
	return temp
		
#gamePacketHandler
#Expected outcome:Reads game JSON and updates values accordingly and sends corresponding packets
def gameJsonHandler(socket,jsonDict):
	if jsonDict["player_id"] == clientID:
		if gameID == -1:
			gameID == jsonDict["game_id"]
		if not gameID == jsonDict["game_id"]:
			print("ERROR: Received packet from wrong game - " + jsonDict["game_id"])
			print("Has correct playerID information,ERROR:Probably server side")
		else:
			cardID = jsonDict["card"]
			hitJson = clientLogic(cardID)
			sendJson(socket,hitJson)
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
def controlJsonHandler(jsonDict):
	print("PLACEHOLDER")

#readJson
#Expected outcome:Determines what type of json packet is and runs the appropriate function
def readJson(jsonDict):
	temp = json.loads(jsonDict)
	#If this doesn't work use
	#json.loads(jsonDict)[0]

	if temp["type": "CONTROL"]:
		controlJsonHandler(jsonDict)
	if temp["type": "GAME"]:
		gameJsonHandler(jsonDict)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 1234)
print ('connecting to %s port %s' % server_address)
sock.connect(server_address)

loginRequest(sock)
joinQueue(sock)

#Socket Loop
try:
	while True:    
		exit = False
		# Loop for packet reading
		amount_received = 0
		amount_expected = len(message)

		while amount_received < amount_expected:
			data = sock.recv(1024)
			amount_received += len(data)
			packet = data.decode()
			readJson(packet)						
		if exit:
			print("Exit is true\n")
			break
finally:    
	print ('closing socket')
	sock.close()
