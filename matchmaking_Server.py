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
tournamentRematch = []
tournamentPlayers = []
tournamentDisconnect = []

#joinTournamentQueue
#Adds client ID to the tournament queue
def joinTournamentQueue(clientID):
    print("TOURNAMENT QUEUE ADDED PLAYER: ",clientID)
    tournamentQueue.append(clientID)

#joinTestQueue
#Client ID is added to the test queue and the time they joined is recorded
def joinTestQueue(clientID):
    print("TEST QUEUE ADDED PLAYER: ",clientID)
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
    print("DEBUG: Couldn't find game_",gameID)
    return None

#mmrEvaluation
#Compares the mmr of two players to see if they can be matched against each other
def mmrEvaluation(queueIndex_1,queueIndex_2,clientIDList,timeList):
    elapsedTime_1 = time.time() - timeList[queueIndex_1]
    elapsedTime_2 = time.time() - timeList[queueIndex_2]
    clientMMR_1 = findClientMMR(clientIDList[queueIndex_1])
    clientMMR_2 = findClientMMR(clientIDList[queueIndex_2])
    print("CLIENTID_1:",clientIDList[queueIndex_1])
    print("CLIENTID_2:",clientIDList[queueIndex_2])
    if clientMMR_1 == -1:
        print("ERROR: Couldn't find mmr of client",clientIDList[queueIndex_1])
        return False
    if clientMMR_2 == -1:
        print("ERROR: Couldn't find mmr of client",clientIDList[queueIndex_2])
        return False
    boundary_1 = (clientMMR_1 - 100 - (elapsedTime_1 * 10) ,clientMMR_1 + 100 + (elapsedTime_1 * 10))
    boundary_2 = (clientMMR_2 - 100 - (elapsedTime_2 * 10) ,clientMMR_2 + 100 + (elapsedTime_2 * 10))
    if boundary_1[0] < boundary_2[1] and boundary_1[0] > boundary_2[0]:
        return True
    elif boundary_1[1] < boundary_2[1] and boundary_1[1] > boundary_2[0]:
        return True
    elif boundary_2[0] < boundary_1[1] and boundary_2[0] > boundary_1[0]:
        return True
    elif boundary_2[1] < boundary_1[1] and boundary_2[1] > boundary_1[0]:
        return True
    return False

#mmrUpdate
#Updates their mmr using Arpad's Elo System
def mmrUpdate(winner,playerList):
    winnerMMR = findClientMMR(winner)
    if winnerMMR == -1:
        print("ERROR: Couldn't find winner's MMR")
        #winnerMMR = 1000
    averageLoserMMR = 0
    numberOfLosers = 0
    for loser in playerList[:-1]:
        if loser == winner:
            continue
        else:
            loserMMR = findClientMMR(loser)
            if loserMMR == -1:
                print("ERROR: Couldn't find loser's MMR")
                continue
            averageLoserMMR += loserMMR
            numberOfLosers += 1
            expectedResultLoser = float(1/(1 + 10 ** ((winnerMMR - loserMMR) / 400)))
            loserNewMMR = int(loserMMR - ((1 - expectedResultLoser) * 24))
            database.updateMMR(loser,loserNewMMR)
    averageLoserMMR = averageLoserMMR / numberOfLosers
    expectedResultWinner = float(1/ (1 + 10 ** ((averageLoserMMR - winnerMMR) /400)))
    winnerNewMMR = int(winnerMMR + ((1 - expectedResultWinner) * 24))
    database.updateMMR(winner,winnerNewMMR)

#terminateGameList
#Removes the playerList from the gamePlayerList
def terminateGameList(gameID):
    playerList = getPlayerList(gameID)
    if playerList in gamePlayerList:
        gamePlayerList.remove(playerList)

#playerDisconnect
#When a play has disconnected we run this function to remove them from the appropriate queue
def playerDisconnect(clientID):
    if clientID in testQueue:
        cIndex = testQueue.index(clientID)
        testQueue.pop(cIndex)
        testQueueTime.pop(cIndex)
    elif clientID in tournamentQueue:
        tournamentQueue.remove(clientID)
    elif clientID in tournamentPlayers:
        tournamentDisconnect.append(clientID)
        tournamentPlayers.remove(clientID)

#notifyFinish
#Removes the game's data from the global vars and updates the mmrValues
#If the game is a tournament game it's added to tournamentFinish
def notifyFinish(gameID,winner):
    playerList = getPlayerList(gameID)
    if winner != -1:
        mmrUpdate(winner,playerList)
    if gameID in tournamentGameID:
        print("TOURNAMENT GAME FINISHED, GameID = ",gameID)
        if winner == -1:
            tournamentRematch.append((gameID,-1))
        else:
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
            tempPlayerList = []
            for index_1 in range (0,maxLength-1):
                player1 = tempQueue[index_1]
                print("Player 1: ",player1)
                tempPlayerList.append(player1)
                for index_2 in range(index_1 + 1,maxLength):
                    if mmrEvaluation(index_1,index_2,testQueue,testQueueTime):
                        for x in tempQueue:
                            print ("TEMPQUEUE: ",x)
                        print("INDEX2: ",index_2)
                        player2 = tempQueue[index_2]
                        print("Player 2 :",player2)
                        tempPlayerList.append(player2)
                    #Maximum amount of players is 8 (7 + Dealer)
                    if len(tempPlayerList) == 4:
                        break
                if(len(tempPlayerList)) > 1:
                    break
            if len(tempPlayerList) > 1:
                stopGame = False
                gameCounter = time.time()
                time.sleep(1)
                for player in tempPlayerList:
                    if player not in testQueue:
                        stopGame = True
                if stopGame == False:
                    ConnMan.start_game(gameCounter,tempPlayerList)
                    gameThread = threading.Thread(target=Blackjack_Server.gameStart,args = (gameCounter,tempPlayerList,False))
                    gameThread.start()
                    for player in tempPlayerList:
                        print("tempPlayerList: ",player)
                        playerIndex = testQueue.index(player)
                        testQueueTime.pop(playerIndex)
                        testQueue.remove(player)
                    tempPlayerList.append(gameCounter)
                    gamePlayerList.append(tempPlayerList)

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
            ConnMan.start_game(gameCounter,tempGPL)
            gameThread = threading.Thread(target = Blackjack_Server.gameStart,args = (gameCounter,tempGPL,True))
            gameThread.start()
            tempGPL.append(gameCounter)
            tournamentGameID.append(gameCounter)
            currentGameID.append(gameCounter)
            gamePlayerList.append(tempGPL)
        while(len(currentLobbyList) != currentPlayerCount/2):
            tempDelete = (None,None)
            for currentGame in currentGameID:
                resetList = False
                for rematch in tournamentRematch:
                    if rematch[0] == currentGame:
                        print("DEBUG: GAME_",tempDelete[0]," rematch")
                        playerList = getPlayerList(rematch[0])
                        newGame = playerList[:-1].copy()
                        gameCounter = time.time()
                        time.sleep(1)
                        ConnMan.start_game(gameCounter,newGame)
                        gameThread = threading.Thread(target = Blackjack_Server.gameStart,args = (gameCounter,newGame,True))
                        gameThread.start()
                        newGame.append(gameCounter)
                        tournamentGameID.append(gameCounter)
                        currentGameID.append(gameCounter)
                        gamePlayerList.append(newGame)
                        terminateGameList(playerList)
                        resetList = True
                        tempDelete = rematch
                        break
                if resetList:
                    break
                for finishedGame in tournamentFinished:
                    if finishedGame[0] == currentGame:
                        tempDelete = finishedGame
                        print("DEBUG: GAME_",tempDelete[0]," has finished")
                        if finishedGame[1] not in currentLobbyList:
                            currentLobbyList.append(finishedGame[1])
                        playerList = getPlayerList(finishedGame[0])
                        for player in playerList:
                            if player == finishedGame[1]:
                                continue
                            else:
                                if player in tournamentPlayers:
                                    tournamentPlayers.remove(player)
                                elif player in tournamentDisconnect:
                                    tournamentDisconnect.remove(player)
                                if player in currentPlayerList:
                                    currentPlayerList.remove(player)
                        terminateGameList(currentGame)
                        resetList = True
                        break
                if resetList:
                    break
            
            if tempDelete != (None,None):
                print("DEBUG: TEMPDELETE = GAME_",tempDelete[0])
                if tempDelete in tournamentFinished:
                    tournamentFinished.remove(tempDelete)
                elif tempDelete in tournamentRematch:
                    tournamentRematch.remove(tempDelete)
                tournamentGameID.remove(tempDelete[0])
                currentGameID.remove(tempDelete[0]) 
                
            tempList = tournamentDisconnect.copy()
            for disconnectedPlayer in tempList:
                if disconnectedPlayer in currentLobbyList:
                    currentLobbyList.remove(disconnectedPlayer)
                    currentPlayerCount -= 2
                if disconnectedPlayer in currentPlayerList:
                    currentPlayerList.remove(disconnectedPlayer)
                    #currentPlayerCount -= 1
                if disconnectedPlayer in tournamentDisconnect:
                    tournamentDisconnect.remove(disconnectedPlayer)
        currentPlayerCount = len(currentLobbyList)
    print("CURRENT PLAYER COUNT BEFORE WINNER")
    print(len(currentPlayerList))
    print(currentPlayerCount)
    for winner in currentPlayerList:
        ConnMan.send_message(winner,{"packet_type": "CONTROL", "subtype" : "TOURNAMENT_WIN","player_id" : winner})
        ConnMan.disconnect_client(winner)

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
                    


                        
