ConnMan documentation
=====================

##JSON message exchange format
the formatting for any message recieved over a socket will be specified by the game documentation.
Game messages can be received by calling `get_game_messsage(game_id)`, where game_id is the games'
id. Any disconnected player will have a message sent to them, as well as a message sent down to both
the matchmaking server and game server.

##Receiving/retrieving a message from ConnMan
To receive/retrieve a message from ConnMan, such as from a client, use the function `get_game_message(game_id)`
to receive/retrieve a message for the matchmaking, use the function `get_match_message()`

##Sending a message to a client
To send a message to a client, use the `send_message(addr, message)` function. Addr will be whatever we use to
uniquely identify the client(currently just using their ip address), and message is a dictionary of formatted json.

##Receiving control messages
Any messages from ConnMan to anything down stream will come in the same form as a packet: an (addr, dict) tuple.
The dictionary will contain the members "type" : "CONTROL", and various subtypes. A new connection will be marked
as subtype "C", and a disconnect will be marked by a subtype "DC". There are, as of yet, no other control messages.

##Ending a game
Please, when a game has ended, call the `end_game(game_id)` function to notify ConnMan. This is purely to keep memory
complexity for the message queues to a minimum.

-----
If there is anything else I've missed, let me know