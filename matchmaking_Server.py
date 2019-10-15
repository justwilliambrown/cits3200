#Python matchmaking Server
import json
import socket
import threading
import select
import sys
import time
import ConnMan
import Blackjack_Server
import database

#Global Variables
tournamentQueue = [] #Contains all the clientids in tournament queue
testQueue = [] #Contains all the clientids in the test queue
testQueueTime = [] #Contains the time a client joined the queue
gamePlayerList = [] #gamePlayerList[][0 - numPlayers + 1] = clientID -> FinalValue = uniqueGameID
tournamentGameID = [] #Contains all gameIDS that are tournament games
tournamentFinished = []
tournamentPlayers = []
tournamentDisconnect = []

#joinTournamentQueue
#Adds client ID to the tournament queue
def joinTournamentQueue(clientID):
    tournamentQueue.append(clientID)

#joinTestQueue
#Client ID is added to the test queue and the time they joined is recorded
def joinTestQueue(clientID):
    testQueue.append(clientID)
    testQueueTime.append(time.time())

#findClientMMR
#Queries the database for the client's mmr
def findClientMMR(clientID):
    return database.getMMR(clientID)

#getPlayerList
#Gets the playerList for the given gameID
def getPlayerList(gameID):
    for game in gamePlayerList:
        if game[-1] == gameID:
            return game
    return None

#mmrEvaluation
#Compares the mmr of two players to see if they can be matched against each other
def mmrEvaluation(queueIndex_1,queueIndex_2,clientIDList,timeList):
    elapsedTime_1 = time.time() - timeList[queueIndex_1]
    elapsedTime_2 = time.time() - timeList[queueIndex_2]
    clientMMR_1 = findClientMMR(clientIDList[queueIndex_1])
    clientMMR_2 = findClientMMR(clientIDList[queueIndex_2])
    if clientMMR_1 == -1:
        print("ERROR: Couldn't find mmr of client" + clientIDList[queueIndex_1])
        return False
    if clientMMR_2 == -1:
        print("ERROR: Couldn't find mmr of client" + clientIDList[queueIndex_2])
        return False
    boundary_1 = (clientMMR_1 - 100 - (elapsedTime_1 * 10) ,clientMMR_1 + 100 + (elapsedTime_1 * 10))
    boundary_2 = (clientMMR_2 - 100 - (elapsedTime_2 * 10) ,clientMMR_2 + 100 + (elapsedTime_2 * 10))
    if boundary_1[0] < bounday_2[1] and boundary_1[0] > boundary_2[0]:
        return True
    elif boundary_1[1] < bounday_2[1] and boundary_1[1] > boundary_2[0]:
        return True
    elif boundary_2[0] < bounday_1[1] and boundary_2[0] > boundary_1[0]:
        return True
    elif boundary_2[1] < bounday_1[1] and boundary_2[1] > boundary_1[0]:
        return True
    return False

#mmrUpdate
#Updates their mmr using Arpad's Elo System
def mmrUpdate(winner,playerList):
    winnerMMR = ConnMan.findClientMMR(winner)
    if winnerMMR == -1:
        print("ERROR: Couldn't find winner's MMR")
        #winnerMMR = 1000
    averageLoserMMR = 0
    numberOfLosers = 0
    for loser in playerList[:-1]:
        if loser == winner:
            continue
        else:
            loserMMR = ConnMan.findClientMMR(loser)
            if loserMMR == -1:
                print("ERROR: Couldn't find loser's MMR")
                continue
            averageLoserMMR += loserMMR
            numberOfLosers += 1
            expectedResultLoser = float(1/(1 + 10 ^ ((winnerMMR - loserMMR) / 400)))
            loserNewMMR = int(loserMMR - ((1 - expectedResultLoser) * 24))
            database.updateMMR(loser,loserNewMMR)
    averageLoserMMR = averageLoserMMR / numberOfLosers
    expectedResultWinner = float(1/ (1 + 10 ^ ((averageLoserMMR - winnerMMR) /400)))
    winnerNewMMR = int(winnerMMR + ((1 - expectedResultWinner) * 24))
    database.updateMMR(winner,winnerNewMMR)

#terminateGameList
#Removes the playerList from the gamePlayerList
def terminateGameList(gameID):
    playerList = getPlayerList(gameID)
    gamePlayerList.remove(playerList)

#playerDisconnect
#When a play has disconnected we run this function to remove them from the appropriate queue
def playerDisconnect(clientID):
    if clientID in testQueue:
        cIndex = testQueue.index(clientID)
        testQueue.pop(cIndex)
        testQueueTime.pop(cIndex)
    elif clientID in tournamentQueue:
        cIndex = tournamentQueue.index(clientID)
        testQueue.pop(cIndex)
        testQueueTime.pop(cIndex)
    elif clientID in tournamentPlayers:
        tournamentDisconnect.append(clientID)
        tournamentPlayers.remove(clientID)

#notifyFinish
#Removes the game's data from the global vars and updates the mmrValues
#If the game is a tournament game it's added to tournamentFinish
def notifyFinish(gameID,winner):
    playerList = getPlayerList(gameID)
    mmrUpdate(winner,playerList)
    if gameID in tournamentGameID:
        tempTuple = (gameID,winner)
        tournamentFinished.append(tempTuple)
    else:
        terminateGameList(gameID)

#packetQueueHandler
#Thread to handle the packet queue
def packetQueueHandler():
    while True:
        msg = ConnMan.get_match_message(False)
        if msg!= None:
            if "Queue" in msg:
                queueType = msg["Queue"]
                if queueType == "Test":
                    if msg["player_id"] not in testQueue:
                        joinTestQueue(msg["player_id"])
                elif queueType == "Tournament":
                    if msg["player_id"] not in tournamentQueue:
                        joinTournamentQueue(msg["player_id"])
                else:
                    requestQueueType = {
                                        "packet_type" : "CONTROL",
                                        "player_id" : msg["player_id"],
                                        "type" : "REQUEST",
                                        "item" : "queueType"
                                        }
                    ConnMan.send_message(msg["player_id"],requestQueueType)

#testQueueHandler
#Thread to handle the test queue
def testQueueHandler():
    while True:
        tempQueue = testQueue.copy()
        tempQueueTime = testQueueTime.copy()
        resetQueue = False
        if len(tempQueue) < 2:
            time.sleep(1)
            #Do nothing
        else:
            maxLength = len(testQueue)
            for index_1 in range (0,maxLength-1):
                tempPlayerList = []
                player1 = tempQueue[index_1]
                tempPlayerList.append(player1)
                for index_2 in range(index_1 + 1,maxLength):
                    if mmrEvaluation(index_1,index_2,testQueue,testQueueTime):
                        player2 = tempQueue[index_2]
                        tempPlayerList.append(player2)
                    #Maximum amount of players is 8 (7 + Dealer)
                    if len(tempPlayerList) == 7:
                        break
                if len(tempPlayerList) > 1:
                    gameCounter = time.time()
                    time.sleep(1)
                    Connman.start_game(gameCounter,tempPlayerList)
                    gameThread = threading.Thread(target=Blackjack_Server.gameStart,args = (gameCounter,tempPlayerList,False))
                    gameThread.start()
                    for player in tempPlayerList:
                        testQueueTime.pop(testQueue.index(player))
                        testQueue.remove(player)
                    tempPlayerList.append(gameCounter)
                    gamePlayerList.append(tempList)
                    resetQueue = True
                    break
                if resetQueue == True:
                    break

#tournamentHandler
#Thread that handles each individual tournament
def tournamentHandler(tPlayerList):
    currentPlayerList = tPlayerList.copy()
    currentLobbyList = tPlayerList.copy()
    initialPlayerCount = len(tPlayerList)
    currentPlayerCount = len(tPlayerList)
    currentGameID = []  #Holds the Game IDS for all the games in the tournament 
    while(currentPlayerCount > 1):
        for i in range (currentPlayerCount//2):
            tempGPL = []
            player1 = currentLobbyList.pop()
            player2 = currentLobbyList.pop()
            tempGPL.append(player1)
            tempGPL.append(player2)
            gameCounter = time.time()
            time.sleep(1)
            ConnMan.start_game(tempCounter,tempList)
            gameThread = threading.Thread(target = Blackjack_Server.gameStart,args = (tempCounter,tempList,True))
            gameThread.start()
            tempList.append(gameCounter)
            tournamentGameID.append(gameCounter)
            currentGameID.append(gameCounter)
            gamePlayerList.append(tempGPL)
            currentLobbyList.remove(player1)
            currentLobbyList.remove(player2)
        while(len(currentLobbyList) != currentPlayerCounter/2):
            tempDelete = (None,None)
            for currentGame in currentGameID:
                resetList = False
                for finishedGame in tournamentFinished:
                    if finishedGame[0] == currentGame:
                        tempDelete == finishedGame
                        currentLobbyList.append(finishedGame[1])
                        playerList = getPlayerList(currentGame)
                        for player in playerList:
                            if player == finishedGame[1]:
                                continue
                            else:
                                if player in tournamentPlayers:
                                    tournamentPlayers.remove(player)
                                else:
                                    tournamentDisconnect.remove(player)
                                if player in currentPlayerList:
                                    currentPlayerList.remove(player)
                        terminateGameList(currentGame)
                        resetList = True
                        break
                if resetList:
                    break
            if tempDelete in tournamentFinished:
                tournamentFinished.remove(tempDelete)
                tournamentGameID.remove(tempDelete[0])
                currentGameID.remove(tempDelete[0])
            
            tempList = tournamentDisconnect.copy()
            for disconnectedPlayer in tempList:
                if disconnectedPlayer in currentLobbyList:
                    currentLobbyList.remove(disconnectedPlayer)
                    currentPlayerCounter -= 2
                    tournamentDisconnect.remove(disconnectedPlayer)
                if disconnectedPlayer in currentPlayerList:
                    currentPlayerList.remove(player)
        currentPlayerCounter = len(currentLobbyList)
    for winner in currentPlayerList:
        ConnMan.send_message(winner,{"packet_type": "CONTROL", "type" : "TOURNAMENT_WIN","player_id" : winner})
        disconnect_client(winner)

#tournamentQueueHandler
#Handles the tournament queue and creates tournaments when 8 players are found
def tournamentQueueHandler():
    while True:
        if len(tournamentQueue) >= 8:
            tourneyTemp = []
            for i in range(8):
                player = tournamentQueue.pop(0)
                tourneyTemp.append(player)
                tournamentPlayers.append(player)
            tournamentThread = threading.Thread(target=tournamentHandler(tourneyTemp))
            tournamentThread.start()

#Start function to start matchmaking server
def start():
    packetQHandler = threading.Thread(target=packetQueueHandler)
    packetQHandler.start()
    testQHandler = threading.Thread(target=testQueueHandler)
    testQHandler.start()
    tournamentQHandler = threading.Thread(target = tournamentQueueHandler)
    tournamentQHandler.start()
                    


                        
