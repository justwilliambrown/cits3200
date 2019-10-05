#Python matchmaking Server
import json
import socket
import threading
import select
import sys
import time
import ConnMan
import Blackjack_Server


#Global Variables
queueCheck = []             #Contains all players who are in some sort of queue(for checking purposes)
tournamentQueue = []        #Contains all the client ids in tournament queue
testQueue = []              #Contains all the client ids in test queue
testQueueTime = []           #Contains the time a client joined the queue
gamePlayerList = []    		#gamePlayerList[][0 - numPlayers + 1] = clientID -> Final value = unique gameID
tournamentGameID = []       #Contains all gameIDS that are tournament games
gameCounter = 10000         #Counter for gameID starts at 10000 #NOTE: Check with Josh that we don't have overlapping IDS just incase
tournamentFinished = []     #Contains the gameIDs and the client ID of who won the finished tournament game. (0 = gameID, 1 = clientID)
tournamentPlayers = []      #Contains all the clientIDS of player who are connected and are currently in a tournament
tournamentDisconnect = []   #Contains the clientIDS of players who've disconnected

#Funtions
#joinTournamentQueue
#Input: Client ID
#Expected outcome : clientID joins the tournament Queue and time joined recorded
def joinTournamentQueue(clientID):
    tournamentQueue.append(clientID)


#joinTestQueue
#Input: Client ID
#Expected outcome : clientID joins the test Queu eand time joined recorded
def joinTestQueue(clientID):
    testQueue.append(clientID)
    testQueue.append(time.time())


#--------------------------------------NOTE-------------------------------------------------------------
#Need to grab mmr from database
#TODO: ask Aidan to pull the MMR info from database along with the client ID when authenticating user
#Store in a list of tuples (ClientID,MMR). This list can be called clientMMR.
#findClientMMR -NOTE:Move this function to the ConnMan
#Input: Client ID
#Output: Client's MMR
clientMMR = []
def findClientMMR(clientID):
    for client in clientMMR:
        if client[0] == clientID:
            return client[1]
    return -1
#--------------------------------------NOTE-------------------------------------------------------------

#getPlayerList
#Input: Game ID
#Output: List containing all players in Game ID
def getPlayerList(gameID):
    for game in gamePlayerList:
        if game[-1] == gameID:
            return game
    return None

#mmrEvaluation
#Input: 2 Different index's of people in test queue
#Output: Boolean(Whether or not the mmr is within the boundaries)
#Calculation:Boundary Starts at 100 mmr Increases by 10 for every second in queue
def mmrEvaluation(queueIndex_1,queueIndex_2,clientIDlist,timeList):
    elapsedTime_1 = time.time() - timeList[queueIndex_1]
    elapsedTime_2 = time.time() - timeList[queueIndex_2]
    clientMMR_1 = ConnMan.findClientMMR(clientIDlist[queueIndex_1])
    clientMMR_2 = ConnMan.findClientMMR(clientIDList[queueIndex_2])
    if clientMMR_1 == -1:
        print("ERROR: Couldn't find mmr of client" + clientIDList[queueIndex_1])
        return False
    if clientMMR_2 == -1:
        print("ERROR: Couldn't find mmr of client" + clientIDList[queueIndex_2])
        return False
    boundary_1 = (clientMMR_1 - 100 - (elapsedTime_1 * 10) ,clientMMR_1 + 100 + (elapsedTime_1 * 10))
    boundary_2 = (clientMMR_2 - 100 - (elapsedTime_2 * 10) ,clientMMR_2 + 100 + (elapsedTime_2 * 10))
    #4 Scenarios
    #Boundary 1 lower limit within boundary 2 limit
    if boundary_1[0] < bounday_2[1] and boundary_1[0] > boundary_2[0]:
        return True
    #Boundary 1 upper limit within boundary 2 limit
    if boundary_1[1] < bounday_2[1] and boundary_1[1] > boundary_2[0]:
        return True
    #Boundary 2 lower limit within boundary 1 limit
    if boundary_2[0] < bounday_1[1] and boundary_2[0] > boundary_1[0]:
        return True
    #Boundary 2 upper limit within boundary 1 limit
    if boundary_2[1] < bounday_1[1] and boundary_2[1] > boundary_1[0]:
        return True
    return False

#mmrUpdate
#Using Arpad's Elo system
#Input: 2 client ID's(First is the winner, second is the loser)
def mmrUpdate(winner,playerList):
    winnerMMR = ConnMan.findClientMMR(winner)
    averageLoserMMR = 0
    numberOfLosers = 0
    for loser in playerList[:-1]:
        if loser == winner:
            continue
        else:
            loserMMR = ConnMan.findClientMMR(loser)
            averageLoserMMR += loserMMR
            numberOfLosers += 1
            float expectedResultLoser = 1 / (1 + 10 ^ ((winnerMMR - loserMMR) / 400))
            int loserNewMMR = loserMMR - ((1 - expectedResultLoser) * 24)
    averageLoserMMR = averageLoserMMR / numberOfLosers
    float expectedResultWinner = 1 / (1 + 10 ^ ((averageLoserMMR - winnerMMR) / 400))
    int winnerNewMMR = winnerMMR + ((1 - expectedResultWinner) * 24)
    #TODO:CODE FOR COMMUNICATING WITH DATABASE TO UPDATE THE VALUES GOES HERE


#terminateGameList
#Input: Game ID
#Expected outcome: Remove the player list for game ID from gamePlayerList
def terminateGameList(gameID):
    playerList = getPlayerList(gameID)
    gamePlayerList.remove(playerList)



#playerDisconnect
#Input: clientID
#Exepected outcome: Removes clientID from the queue
def playerDisconnect(clientID):
    #Try removing from test queue first
    #If they're not in test queue try the tournament queue
    if clientID in testQueue:
        cIndex = testQueue.index(clientID)
        testQueue.pop(cIndex)
        testQueueTime.pop(cIndex)
        queueCheck.remove(clientID)
    if clientID in tournamentQueue:
        cIndex = tournamentQueue.index(clientID)
        tournamentQueue.pop(cIndex)
        queueCheck.remove(clientID)
    if clientID in tournamentPlayers:
        tournamentDisconnect.append(clientID)
        tournamentPlayers.remove(clientID)

#notifyFinish
#Input:Game ID, Winner
#Expected outcome :Remove all the data that contains that game's information and update the mmr values
#If the game is a tournament game add it to tournamentFinished
def notifyFinish(gameID,winner):
    playerList = getPlayerList(gameID)
    mmrUpdate(winner,playerList)
    if gameID in tournamentGameID:
        tempTuple = (gameID,winner)
        tournamentFinished.append(tempTuple)
    else:
        terminateGameList(gameID)

#testQueueHandler
#Input: No input
#Function: Handles the test queue and matches people into games
#Is designed to be run continuosly(24/7) on it's own thread
#Needs to notify the ConnManager Module when a lobby has been filled
#PLACEHOLDER: For now I've set it up so that all the lobbies only contain 2 people
def testQueueHandler():
    while True:
        #Check to see if someone wants to join the queue
        msg = ConnMan.get_match_message(False)
        if msg != None:
            clientID = msg["player_id"]
            if clientID not in testQueue:
                jointestQueue(clientID)
        #Clone the queues first to avoid memory problems
        tempQueue = testQueue.copy()
        tempQueueTime = testQueueTime.copy()
        resetQueue = False
        #Check to see if there are enough players to start the game
        if len(tempQueue) < 2:
            continue
        else:
            maxLength = len(testQueue)
            for index_1 in range(0,maxLength - 1):
                for index_2 in range(index_1 + 1,maxLength):
                    if mmrEvaluation(index_1,index_2,testQueue,testQueueTime):
                        tempList = []
                        global gameCounter
                        tempQueue2 = tempQueue.copy()
                        player1 = tempQueue.pop(index_1)
                        player2 = tempQueue2.pop(index_2)
                        tempList.append(player1)
                        tempList.append(player2)
                        tempCounter = gameCounter
                        gameCounter += 1
                        ConnMan.start_game(tempCounter,tempList)
                        gameThread = threading.Thread(target=Blackjack_Server.gameStart,args = (tempCounter,tempList,False))
                        gameThread.start()
                        tempList.append(tempCounter)
                        gamePlayerList.append(tempList)
                        testQueue.remove(player1)
                        testQueue.remove(player2)
                        resetQueue = True
                        break
                    if resetQueue == True:
                        break
                if resetQueue == True:
                    break

#tournamentHandler
#Input: Array containing 16 player IDs to host a tournament with
#Expected outcome: Handles the entirety of the tournament
def tournamentHandler(tPlayerList):
    currentPlayerList = tPlayerList.copy()
    currentLobbyList = tPlayerList.copy()
    initialPlayerCount = len(tPlayerList)
    currentPlayerCount = len(tPlayerList)
    currentGameID = [] #Holds the ID for games that are currently running
    for i in range(currentPlayerCount):
        playerWinCounter[i] = 0
    while(currentPlayerCounter <= 1):
        for i in range (currentPlayerCount//2):
            tempList = []
            global gameCounter
            player1 = currentLobbyList.pop()
            player2 = currentLobbyList.pop()
            tempList.append(player1)
            tempList.append(player2)
            tempCounter = gameCounter
            gameCounter += 1
            ConnMan.start_game(tempCounter, tempList)
            gameThread = threading.Thread(target = Blackjack_Server.gameStart,args = (tempCounter,tempList,True))
            gameThread.start()
            tempList.append(tempCounter)
            tournamentGameID.append(tempCounter)
            currentGameID.append(tempCounter)
            gamePlayerList.append(tempList)
            currentLobbyList.remove(player1)
            currentLobbyList.remove(player2)
        #Wait to receive notification that all  x games have been terminated
        while(len(currentLobbyList) != currentPlayerCounter/2):
            #CODE TO CHECK IF A GAME HAS ENDED AND TO ADD WINNER BACK TO CURRENTLOBBYLIST
            tempDelete = (None,None)
            for currentGame in currentGameID:
                resetList = False
                for finishedGame in tournamentFinished:
                    if finishedGame[0] = currentGame:
                        tempDelete = finishedGame
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
                                currentPlayerList.remove(player)
                                currentPlayerCount -= 1
                        terminateGameList(currentGame)
                        resetList = True
                        break
                if(resetList):
                    break
            tournamentFinished.remove(tempDelete)
            tournamentGameID.remove(tempDelete[0])
            currentGame.remove(tempDelete[0])
            tempList = tournamentDisconnect.copy()
            for disconnectedPlayer in tempList:
                #If the game is still running don't do anything
                #Otherwise they disconnected while in the lobby which means the lobby number needs to decrease
                if disconnectedPlayer in currentLobbyList:
                    currentLobbyList.remove(disconnectedPlayer)
                    currentPlayerCounter -= 2
                    tournamentDisconnect.remove(disconnectedPlayer)
            #----------------------------------------------------------------------------
            time.sleep(1)
        currentPlayerCounter = len(currentLobbyList)
    #Tournament has now ended

#tournamentQueueHandler
#Input: No input
#Function: Handles the test queue and matches people into games
#Is designed to be run continuosly(24/7) on it's own thread
#Placeholder : 16 player tournaments single elimination style
def tournamentQueueHandler():
    while True:
        #No mmr matching as soon as there are 16 people in queue create a tournament
        if len(tournamentQueue) >= 16:
	    tourneyTemp = []
            for i in range(16):
                player = tournamentQueue.pop(0)
                tourneyTemp.append(player)
                tournamentPlayers.append(player)
            tournamentThread = threading.Thread(target = tournamentHandler(tourneyTemp))
            tournamentThread.start()


def start():
	testQHandler = threading.Thread(target=testQueueHandler)
	testQHandler.start()
        tournamentQHandler = threading.Thread(target = tournamentQueueHandler)
        tournamentQHandler.start()
