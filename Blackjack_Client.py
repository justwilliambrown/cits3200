import random
import socket
import threading
import json
import math

#Global variables
clientID = '-1'
balance = 0
cardTotal = {}
gameID = -1
exit = False
cardSeen = []
cardHold = []
packetQueue = []
currentBet = 0

#sendJson
#Input:Socket,Dictionary
#Outcome: Encodes and sends JSON
def sendJson(sock,jsonDict):
    print("SENDING",jsonDict)
    sock.send(jsonDict)

#loginRequest
#Outcome: Sends login request to server
def loginRequest(sock):
    username = input("Username:")
    password = input("Password:")
    loginDetails = {
            "user" : username,
            "pass" : password,
    }
    jsonLogin = json.dumps(loginDetails).encode()
    sendJson(sock,jsonLogin)

#joinQueue
#Expected outcome:Sends queue request to server
def joinQueue(sock):
    qType = input("Queue type: Test , Tournament")
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
    global clientID
    global cardTotal
    if clientID == '-1':
        #Initialising login
        if jsonDict["subtype"] == "loginRequest":
            loginRequest(sock)
        elif jsonDict["subtype"] == "loginDeny":
            print("ERROR: Login details were incorrect no terminating program")
            exit = True
        elif jsonDict["subtype"] == "loginAccept":
            clientID = jsonDict["id"]
            print("Succesfully logged in as ID :",clientID)
            #Now pick a queue type to join
            joinQueue(sock)
    elif jsonDict["player_id"] == clientID:
        if "subtype" in jsonDict:
            if["subtype"] == "DC":
                exit = True
        if "type" in jsonDict:
            if jsonDict["type"] == "OPENING_BALANCE":
                gameID = jsonDict["game_id"]
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
                        tempDump.json.dumps(temp).encode()
                        sendJson(sock,tempDump)
                    elif jsonDict["item"] == "queueType":
                        joinQueue(sock)
                    elif jsonDict["item"] == "move":
                        if cardTotal[clientID] < 17:
                            temp = {
                                    "packet_type" : "GAME",
                                    "MOVE": "HIT",
                                    "player_id" : clientID,
                                    "game_id" : gameID,
                                    "CONTROL": True
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
                                exit = True
                        elif jsonDict["move"] == "WIN":
                            balance += currentBet
                            currentBet = 0
                elif jsonDict["type"] == "GAME_LOSS":
                    print("You've lost")
                    exit = True
                elif jsonDict["type"] == "VICTORY":
                    print("Congratulations you've won")
                    exit = True
                elif jsonDict["type"] == "TOURNAMENT_WIN":
                    print("Congratulations you've won the entire tournament")
                    exit = True

#Read Json
#Function:Determins what type of json packet it calls the appropriate function
def readJson(jsonDict,sock):
    print("NEW JSON: ",jsonDict)
    if jsonDict["packet_type"] == "CONTROL":
        controlJsonHandler(jsonDict,sock)
    elif jsonDict["packet_type"] == "GAME":
        gameJsonHandler(jsonDict,sock)

#Packet Queue Handler
#Function: Thread to process the packets in the queue
def packetQueueHandler():
    while True:
        if len(packetQueue) != 0:
            tempPacket = packetQueue.pop(0)
            print("PACKET RECEIVED: ",tempPacket)
            readJson(tempPacket,sock)
        if exit:
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
            pQHandler = threading.Thread(target=packetQueueHandler)
            pQHandler.start()
        message = sock.recv(4096)
        amount_received = 0
        amount_expected = len(message)

        while amount_received < amount_expected:
            amount_received += len(message)
            packet = message.decode()
            print("PRE JSON LOADS(PACKET): ",packet)
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
            else:
                packetJson = json.loads(packet)
                print("POST JSON LOADS(PACKET): ",packetJson)
                packetQueue.append(packetJson)
        if exit:
            print("EXITING PROGRAM\n")
            break
finally:
    print("Closing socket")
    sock.close()
