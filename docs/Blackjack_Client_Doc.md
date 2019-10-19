#Documentation for Blackjack Client

## Functions
**sendJson(sock,jsonDict)**
Takes a json dictionary as input and sends the message through the given socket.

**loginRequest(sock)**
Requests username and password from user and sends it as a json dictionary to the given socket.

**joinQueue(sock)**
Requests either "Test" or "Tournament" input from user to determine the queue type for client to queue in. Then sends the request to be placed in the queue through the given socket.

**updateState(cardID,playerID)**
Updates the state of the of the game using the given cardID and playerID

**gameJsonHandler(jsonDict,sock)**
Function to handle all "Game" type packets(Usually updating the game state in some form)

**controlJsonHandler(jsonDict,sock)**
Function to handle all "Control" type packets(Usually taking some form of action based on the packet given), it's also where the "Agent" code is stored.

**readJson(jsonDict,sock)**
Reads the json dictionary and determins what type of packet it is, it then calls the appropriate function for that packet

**packetQueueHandler()**
Function which runs on a seperate thread, this function processes all the packets that are in the packet queue

**Main Body**
Establishes a socket connection with the server that is set in server_address, it then creates a thread to handle the packet queue. Whenever a packet is received it adds the packet to the packet queue. 
