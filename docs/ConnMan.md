ConnMan documentation
=====================

##JSON message exchange format
the formatting for any message recieved over a socket will be specified by the game documentation. Game messages can be received by calling `get_game_messsage(game_id)`, where game_id is the games' id. Any disconnected player will have a message sent to them, as well as a message sent down to both
the matchmaking server and game server.

##Receiving/retrieving a message from ConnMan
To receive/retrieve a message from ConnMan, such as from a client, use the function `get_game_message(game_id)` to receive/retrieve a message for the matchmaking, use the function `get_match_message()`

##Sending a message to a client
To send a message to a client, use the `send_message(addr, message)` function. Addr will be whatever we use to uniquely identify the client(currently just using their ip address), and message is a dictionary of formatted json.

##Receiving control messages
Any messages from ConnMan to anything down stream will come in the same form as a packet: an (addr, dict) tuple.The dictionary will contain the members "type" : "CONTROL", and various subtypes. A new connection will be marked as subtype "C", and a disconnect will be marked by a subtype "DC". There are, as of yet, no other control messages.

##Starting and ending a game
Please, when a game has ended, call the `end_game(game_id, clientList)` function to notify ConnMan. It expects the game id, as well as a list (really, anything that can be iterated through) of the client ids that are in that game. This is purely to keep memory complexity for the message queues to a minimum. The same goes for `start_game(game_id, clientList)`

Function Documentation
====

##recv_all(sock)
wrapper function for the socket receive function, designed for receiving an entire JSON object, rather than an "expected amount". Expects a socket object for its' argument

##start()
begins the thread for the listen socket, and accepting connections.

##client_disconnected(addr)
Used by the client handling thread (described later in this document) for notifying games and the matchmaking server of clients disconnecting. Should not be called from outside ConnMan. The paramater addr is expected to be the integer client id.

##disconnect_client(addr)
To be used for disconnecting a client from the service. The parameter addr is expected to be the integer client id of the client wanting to be disconnected.

##send_message(addr, message)
Used for sending a message down to a client, or to broadcast a message down to all clients in a specific game. The parameter addr is expected to be the integer client id, and message is expected to be a dictionary, representing a JSON object to be sent down to the client. To broadcast a message, set "type" in message to be 'BROADCAST', and it will broadcast that packet to all players in the game specicified by the 'game_id' field in message.

##get_game_message(game_id, blocking=False)
retrieves a message from the message queue from a specific game, that has been received from a client. game_id is expected to be the games ID, and blocking is an optional parameter that specifies whether or not the call will block. If blocking is false, as by default, if the queue is empty it will return None, otherwise the oldest message in the queue will be returned. If blocking is true, then the call will only return when there is an item in the queue.

##get_match_message(blocking=False)
Used to get connection notifications for the matchmaking server. Blocking is as described above.

##start_game(game_id, clientlist)
Used to set up the data structures for sending and receiving messages for specific games. game_id is the integer game ID, and clientlist is any interable populated with the integer client IDs.

##end_game(game_id, client list)
Opposite to the above, used to tear down the data structures for sending and receiving from specific games. Parameters are same as start_game

ListenServer
====
This class is in charge of accepting connections from new clients, and nothing else. It simply accepts connections, and passes it along to the ClientHandle class.

ClientHandle
====
This class is responsible for authenticating a client, as well as receiving the messages and storing it in the various message queues.

Known Bugs
===
If there are simultaneous requests to the database, the MySQL database will close any further connections. This was an error that was discovered approximately 26 hours before submission was due, and the decision was made that an attempt to implement a queue in order to fix it ran a higher risk of causing even more issues. The issue was discovered by attempting to connect multiple clients via a bash script without a sleep, when a ```sleep 2``` was put into the bash script it ran without issue.
