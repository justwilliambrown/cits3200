#Python matchmaking Server
import json
import socket
import select
import sys
import time
from thread import*
import ConnMan

#TODO: Document functionality for each function up here for ease of use
#Functions and their purpose
#joinTournamentQueue
#joinTestQueue
#mmrEvaluation
#getPlayerList
#terminateGameList
#playerDisconnectQueue
#findPlayerGame
#PlayerDisconnectGame
#testQueueHandler
#tournamentHandler
#tournamentQueueHandler

#Global Variables
queueCheck = []             #Contains all players who are in some sort of queue(for checking purposes)
tournamentQueue = []        #Contains all the client ids in tournament queue
tournamentQueueTime = []    #Contains the time a client joined the queue
testQueue = []              #Contains all the client ids in test queue
testQueuTime = []           #Contains the time a client joined the queue
gamePlayerList = [][]       #gamePlayerList[Game ID][0 - numPlayers] = clientID -> Index 0 = unique gameID
tournamentGameList = [][]   #tournamentGameList[TournamentID][0-Number of games] = gameID
tournamentPGC = [][]        #tournamentPlayerGameCounter[TournamentID][2] -> 0 = clientID 1 = Number of games won
gameCounter = 10000         #Counter for gameID starts at 10000 #NOTE: Check with Josh that we don't have overlapping IDS just incase
tournamentCounter = 1000    #Counter for tournament ID starts at 1000
#Funtions
#joinTournamentQueue
#Input: Client ID
#Expected outcome : clientID joins the tournament Queue and time joined recorded
def joinTournamentQueue(clientID)
    tournamentQueue.append(clientID)
    tournamentQueueTIme.append(time.time())


#joinTestQueue
#Input: Client ID
#Expected outcome : clientID joins the test Queu eand time joined recorded
def joinTestQueue(clientID)
    testQueue.append(clientID)
    testQUeue.append(time.time())


#--------------------------------------NOTE-------------------------------------------------------------
#Need to grab mmr from database
#TODO: ask Aidan to pull the MMR info from database along with the client ID when authenticating user
#Store in a list of tuples (ClientID,MMR). This list can be called clientMMR.
#findClientMMR -NOTE:Move this function to the ConnMan
#Input: Client ID
#Output: Client's MMR
def findClientMMR(clientID)
    for client in clientMMR:
        if client[0] == clientID:
            return clientMMR[index][1]
    return -1
#--------------------------------------NOTE-------------------------------------------------------------


#mmrEvaluation 
#Input: 2 Different index's of people in test queue
#Output: Boolean(Whether or not the mmr is within the boundaries)
#Calculation:Boundary Starts at 100 mmr Increases by 10 for every second in queue       
def mmrEvaluation(queueIndex_1,queueIndex_2,clientIDlist,timeList)
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

#getPlayerList
#Input: Game ID
#Output: List containing all players in Game ID
def getPlayerList(gameID)
    return gamePlayerList[gameID]

#terminateGameList
#Input: Game ID
#Expected outcome: Remove the player list for game ID from gamePlayerList
def terminateGameList(gameID)
    gamePlayerList.pop(gameID)

#playerDisconnectQueue
#Input: clientID
#Exepected outcome: Removes clientID from the queue
def playerDisconnectQueue(clientID)
    #Try removing from test queue first
    #If they're not in test queue try the tournament queue
    try:
        testQueue.remove(clientID)
        queueCheck.remove(clientID)
    except:
        tournamentQueue.remove(clientID)
        queueCheck.reove(clientID)
 #This case should never happen 
 #   except:
 #       print("playerDisconnectQueue - ERROR: Client_" + clientID + "couldn't be found in either queue")

#findPlayerGame
#Input: clientID
#Output: Game ID of player
def findPlayerGame(clientID)
    for game in gamePlayerList:
        try:
            game.index(clientID)
        except ValueError:
            continue
    
#PlayerDisconnectGame
#Input: Client ID
#Expected outcome: Removes clientID from the gamelist that they're in
def playerDisconnectGame(clientID)
    gameID = findPlayerGame(clientID)
    gamePlayerList[gameID].remove(clientID)

#--------------------------------------NOTE-------------------------------------------------------------
#NOTE: Move this function onto the ConnMan
#gameCreate
#Input: List of clientIDS
#Expected outcome: Using the list of it creates a thread that hosts a game and handles all logic for all clientIDS in list
def gameCreate #Function will be used for integration on monday
#--------------------------------------NOTE-------------------------------------------------------------

#testQueueHandler
#Input: No input
#Function: Handles the test queue and matches people into games
#Is designed to be run continuosly(24/7) on it's own thread
#Needs to notify the ConnManager Module when a lobby has been filled
#PLACEHOLDER: For now I've set it up so that all the lobbies only contain 2 people
def testQueueHandler
    while True:
    #Clone the queues first to avoid memory problems 
    tempQueue = testQueue.copy()
    tempQueueTime = testQueueTime.copy()
    resetQueue = False
        for index_1 in range(0,len(this.tempQueue)):
            for index_2 in range(index_1 + 1,len(tempQueue)):
                if mmrEvaluation(index_1,index_2,testQueue,testQueueTime):
                    tempList = []
                    tempList.append(gameCounter)
                    gameCounter += 1
                    tempList.append(tempQueue[index_1])
                    tempList.append(tempQueue[index_2])
                    gamePlayerList.append(tempList)
                    ConnMan.gameCreate(tempList)
                    testQueue.remove(tempQueue[index_1])
                    testQueue.remove(tempQueue[index_2])
                    resetQueue = True
                if resetQueue = True:
                    break
            if resetQueue = True:
                break

#tournamentQueueHandler
#Input: No input
#Function: Handles the test queue and matches people into games
#Is designed to be run continuosly(24/7) on it's own thread
#Placeholder : 16 player tournaments single elimination style

    while True:
    #Clone the queues first to avoid memory problems
        tempQueue = tournamentQueue.copy()
        tempQueueTime = tournamentQueueTime.copy()
        #No mmr matching as soon as there are 16 people in queue create a tournament
        if len(tempQueue) == 16:
            tournamentQueue.clear()
            tournamentQueueTime.clear()
            
#tournamentHandler

