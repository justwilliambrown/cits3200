## Documentation for Blackjack Client

## Functions
**sendJson(sock,jsonDict)**

Takes a json dictionary as input and sends the message through the given socket.

**recv_all(sock)** 

Wrapper function for the socket receive function, designed for receiving an entire JSON object, rather than an "expected amount". Expects a socket object for its' argument

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

**Overview**

INITIALISATION
Client first establishes connection with server and receives a login request packet.
Client calls loginRequest function which requests user details and sends said details to the server.
Client receives loginAccept/loginDeny packet, client then calls joinQueue function, the client then requests a "Test" / "Tournament" input from user and sends queue type to the server.
Client is then placed into a queue server side, and hangs until it receives another packet from the server.

Playing a game
Server calls the playround function.Client receives a reset packet, and a card is drawn (and then put back on the other side of the deck) for each player. Client receives this card. A card is similarly dealt for the dealer, and also sent to all players. A second card is dealt to each player, and transmitted to all players. The second card for the dealer is dealt, but NOT transmitted to any player.


Each player is then sent a request for a bet amount for the hand. If the player responds with a number that is greater than their current account balance, it is replaced by their current account balance. If the bet amount provided is less than or equal to 0, it will be replaced by half of their current account balance.  


From there, a request is sent to each player to find out whether they want to stand or hit. If they choose to hit, a card is dealt to them, and transmitted to all players. The total value of their cards are checked, and if it is over 21, they are eliminated. This procedure occurs for each player until all players either stand or are eliminated.  


Following this, the second card dealt to the dealer earlier is transmitted to all players, and the dealer will hit until it reaches a soft 17. Once that is reached (or the dealer goes bust), it is compared against the totals of all of the other players. If the dealer busts, all players who remain in are paid out their bet amount. If the player has a higher total than the dealer, the player is paid out their bet amount. If the player has a lower total than the dealer, the player loses their bet amount.


