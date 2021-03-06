import random
import socket
import threading
import json
import math

#Global variables
clientID = '-1' #The client's ID
balance = 0     #The current balance of the client
cardTotal = {}  #The total value of cards player x holds(x is the key)
gameID = -1     #The current game ID
exitBoolean = False #Boolean for disconnection purposes
cardSeen = []   #All the cards a client has seen in a round(includes client's own cards)
cardHold = []   #Cards held by the client
packetQueue = []  #List that stores all the packets client has to read
currentBet = 0  #The amount that is currently bet in the round by client

class SocketClosedException(Exception):
	pass

class IncorrectPacketFormatException(Exception):
	pass

#recv_all Function to handles message receives
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


#sendJson
#Input:Socket,Dictionary
#Outcome: Encodes and sends JSON
def sendJson(sock,jsonDict):
    print("SENDING",jsonDict)
    sock.send(jsonDict)

#loginRequest
#Outcome: Sends login request to server
def loginRequest(sock):
    username = input("Username: ")
    password = input("Password: ")
    loginDetails = {
            "user" : username,
            "pass" : password,
    }
    jsonLogin = json.dumps(loginDetails).encode()
    sendJson(sock,jsonLogin)

#joinQueue
#Expected outcome:Sends queue request to server
def joinQueue(sock):
    qType = input("Queue type: Test , Tournament: ")
    while qType != "Test" and qType != "Tournament":
        print("Error: Invalid Response")
        qType = input("Select 'Test' or 'Tournament'")
    qDict = {
            "Queue" : qType,
            "player_id": clientID
    }
    jsonQueue = json.dumps(qDict).encode()
    sendJson(sock,jsonQueue)

#updateState
#Expected outcome: Updates the state of the game
def updateState(cardID,playerID):
    global cardTotal
    #If the player hasn't been added to cardTotal add player to cardTotal
    if playerID not in cardTotal:
        cardTotal[playerID] = 0
    #Read the cardID and update the cardTotal for the player accordingly
    cardSeen.append(cardID)
    #If it's the client add the card to it's hand
    if playerID == clientID:
        cardHold.append(cardID)
    value = cardID[0]
    if value == 'J' or value == 'Q' or value == 'K':
        cardTotal[playerID] += 10
    if value == '9':
        cardTotal[playerID] += 9
    if value == '8':
        cardTotal[playerID] += 8
    if value == '7':
        cardTotal[playerID] += 7
    if value == '6':
        cardTotal[playerID] += 6
    if value == '5':
        cardTotal[playerID] += 5
    if value == '4':
        cardTotal[playerID] += 4
    if value == '3':
        cardTotal[playerID] += 3
    if value == '2':
        cardTotal[playerID] += 2
    if value == '1':
        if cardID[1] == '0':
            cardTotal[playerID] += 10
        else:
            cardTotal[playerID] += 1

#Game packet handler
#Function:Handles the game packets
def gameJsonHandler(jsonDict,sock):
    global gameID
    print("gameJsonGAMEID: ",gameID) 
    if jsonDict["game_id"] == gameID:
        if jsonDict["type"] == "RESET":
            cardTotal.clear()
            cardSeen.clear()
            cardHold.clear()
        else:
            cardID = jsonDict["card"]
            playerID = jsonDict["player_id"]
            updateState(cardID,playerID)
    elif jsonDict["game_id"] != gameID:
        print("ERROR:Received packet from wrong GAMEID: " , jsonDict["game_id"])
        print("Client's game ID is :",gameID)

#Control Json Handler
#Function:Handles the control packets
#AGENT CODE HERE
def controlJsonHandler(jsonDict,sock):
    global balance
    global exitBoolean
    global clientID
    global cardTotal
    global currentBet
    global gameID
    if clientID == '-1':
        #Initialising login
        if jsonDict["subtype"] == "loginRequest":
            loginRequest(sock)
        elif jsonDict["subtype"] == "loginDeny":
            print("ERROR: Login details were incorrect no terminating program")
            exitBoolean = True
        elif jsonDict["subtype"] == "loginAccept":
            clientID = jsonDict["id"]
            print("Succesfully logged in as ID :",clientID)
            #Now pick a queue type to join
            joinQueue(sock)
    elif jsonDict["player_id"] == clientID:
        if "subtype" in jsonDict:
            if["subtype"] == "DC":
                exitBoolean = True
            if["subtype"] == "TOURNAMENT_WIN":
                exitBoolean = True
        if "type" in jsonDict:
            if jsonDict["type"] == "OPENING_BALANCE":
                global gameID
                gameID = jsonDict["game_id"]
                #print("Opening Balance gameID: ",jsonDict["game_id"])
                print("Set game ID:" , gameID)
                balance = jsonDict["BALANCE"]
                cardTotal.clear()
                cardSeen.clear()
                cardHold.clear()
            elif jsonDict["type"] == "LOBBY":
                print("CONGRATULATIONS YOU'VE WON")
                print("You'll now be placed into the lobby for your next match")
            elif gameID == jsonDict["game_id"]:
                #-------------------------------------------------------------------
                #AGENT LOGIC HERE
                if jsonDict["type"] == "REQUEST":
                    if jsonDict["item"] == "BETAMT":
                        currentBet = 10
                        temp = {
                                "packet_type" : "CONTROL",
                                "BETAMT" : currentBet,
                                "player_id" : clientID,
                                "game_id": gameID
                                }
                        tempDump = json.dumps(temp).encode()
                        sendJson(sock,tempDump)
                    elif jsonDict["item"] == "queueType":
                        joinQueue(sock)
                    elif jsonDict["item"] == "move":
                        if cardTotal[clientID] < 17:
                            temp = {
                                    "packet_type" : "GAME",
                                    "MOVE": "HIT",
                                    "player_id" : clientID,
                                    "game_id" : gameID
                                    }
                            tempDump = json.dumps(temp).encode()
                            sendJson(sock,tempDump)
                            print("CARD TOTAL: ",cardTotal[clientID])
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
                            print("CARD TOTAL: ",cardTotal[clientID])
                            print("STAND")
                #----------------------------------------------------------------------
                elif jsonDict["type"] == "BROADCAST":
                    if "move" in jsonDict:
                        if (jsonDict["move"] == "ELIMINATED" or jsonDict["move"] == "LOSS"):
                            balance -= currentBet
                            currentBet = 0
                            if balance == 0:
                                print("Balance is 0 you've lost")
                                #exitBoolean = True
                        elif jsonDict["move"] == "WIN":
                            balance += currentBet
                            currentBet = 0
                elif jsonDict["type"] == "GAME_LOSS":
                    print("You've lost")
                    exitBoolean = True
                elif jsonDict["type"] == "VICTORY":
                    print("Congratulations you've won")
                    exitBoolean = True

#Read Json
#Function:Determins what type of json packet it calls the appropriate function
def readJson(jsonDict,sock):
    #print("NEW JSON: ",jsonDict)
    if jsonDict["packet_type"] == "CONTROL":
        controlJsonHandler(jsonDict,sock)
    elif jsonDict["packet_type"] == "GAME":
        gameJsonHandler(jsonDict,sock)

#Packet Queue Handler
#Function: Thread to process the packets in the queue
def packetQueueHandler(sock):
    global exitBoolean
    global packetQueue
    while True:
        #print("PQH Handler")
        if len(packetQueue) != 0:
            tempPacket = packetQueue.pop(0)
            print("PACKET RECEIVED: ",tempPacket)
            readJson(tempPacket,sock)
            #print("POST readJSON")
        if exitBoolean == True:
            print("Exiting packet Queue Thread\n")
            break

#Socket Connection 
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost',3001)
print('Connecting to %s port %s' %server_address)
sock.connect(server_address)
first = True
try:
    while True:
        if first == True:
            first = False
            pQHandler = threading.Thread(target=packetQueueHandler,args=(sock,))
            pQHandler.start()
        message = recv_all(sock)
        amount_received = 0
        amount_expected = len(message)
        #print("MESSAGE RECEIVED")
        while amount_received < amount_expected:
            amount_received += len(message)
            packet = message
            #print("PRE JSON LOADS(PACKET): ",packet)
            packetCount = packet.count("{")
            if(packetCount > 1):
                packetSplit = packet.split("}",packetCount -1)
                for temp in packetSplit:
                    if(temp[len(temp) -1] != '}'):
                        load = temp + '}'
                    else:
                        load = temp
                    #print("LOAD: ",load)
                    packetJson = json.loads(load)
                    #print("POST JSON LOADS(PACKET): ",load)
                    packetQueue.append(packetJson)
                    if "player_id" in packetJson:
                        if "subtype" in packetJson:
                            if packetJson["player_id"] == clientID:
                                if packetJson["subtype"] == "DC":
                                    exitBoolean = True
                                if packetJson["subtype"] == "VICTORY_WIN":
                                    exitBoolean = True
            else:
                packetJson = json.loads(packet)
                #print("POST JSON LOADS(PACKET): ",packetJson)
                packetQueue.append(packetJson)
                if "player_id" in packetJson:
                    if "subtype" in packetJson:
                        if packetJson["player_id"] == clientID:
                            if packetJson["subtype"] == "DC":
                                exitBoolean = True
                            if packetJson["subtype"] == "VICTORY_WIN":
                                exitBoolean = True
        if exitBoolean == True:
            print("EXITING PROGRAM\n")
            exit()
finally:
    print("Closing socket")
    sock.close()
