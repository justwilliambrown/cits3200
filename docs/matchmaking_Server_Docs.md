# Documentation for matchmakingServer.py

## Functions
**joinTournamentQueue(clientID)**
Adds Client to the tournament matchmaking queue.

**joinTestQueue(clientID)**
Adds Client to the test matchmaking queue.

**findClientMMR(clientID)**
Finds the matchmaking ranking for the client by querying the database.

**mmrEvaluation(queueIndex_1,queueIndex_2,clientIDList,timeList)**
Compares the matchmaking ranking for two players to check if it's within an acceptable range to match them against each other.

**mmrUpdate(winner,playerList)**
Updates the mmr of all players in a game.Run after a game is finished.

**getPlayerList(gameID)**
Gets the list of players that are in the given game ID.

**terminateGameList(gameID)**
Removes the game's stored player list data from the server.Run after a game is finished.

**playerDisconnect(clientID)**
Called by other modules(mainly ConnMan and Blackjack Server) to notify the matchmaking server that a player has disconnected

**notifyFinish(gameID,winner)**
Used by the Blackjack Server to notify the matchmaking server that a game is completed. This function updates the mmr and terminates the player list by calling mmrUpdate and terminateGameList.

**packetQueueHandler()**
Function that runs on a thread to handle all the packets in the ConnMan.connectMsgQueue by calling ConnMan.get_match_message().Reads the packet and determins whether it is a "Test" or "Tournament" queue request packet. If it's neither request the queue type from the user again.

**testQueueHandler()**
Function that runs on a thread to handle all the clients in the test Queue. Whenever there are 2 or more players in the testQueue it creates a game for those players if the mmrEvaluation function determines them to be within each other's skill level.Creates games up to 7 players + 1 dealer.

**tournamentHandler(tPlayerList)**
Function that runs on a thread, this thread handles an entire tournament from start to finish on it's own. 
This is done by repeatedly creating games whenever half as many people are in the tournament lobby as there was previously. When there is only one player in the lobby it sends a tournament victory packet to that player and terminates the thread. 

**tournamentQueueHandler()**
Function that runs on a thread to handle all the clients in the tournament queue. Default setup is 8 players in a single elimination format style tournament. Creates a thread for tournamentHandler whenever there are  8 players in the queue.

**start()**
Function that starts the threads for the tournamentQueueHandler and testQueueHandler.
