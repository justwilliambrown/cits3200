# Documentation giving an overview of the Blackjack Server Implementation


## Functions
**disconnectHandle(playerid)**
In: Playerid. Out: void.  
Called when a player disconnects. Takes in the id of the player who has disconnected, and adds them to the playersEliminated list which will be used at the end of a round to remove that player from the various data structures

**receive(gameID, playerID)**
In: gameID, playerID. Out: message from that player.  
Interacts with the connection manager to receive messages from the players. Does a couple of checks to make sure that the message isn't null, and is from the right player.

**send(data)**
In: dictionary to be converted to JSON and sent. Out: void.  
Interacts with the connection manager to send data to clients.

**populateDeck()**
In: void. Out: Shuffled deck of cards.  
Generates a list of strings, representing cards with the format "value" - "suit". Shuffles the list randomly.

**calculateTotals(cardsHeld)**
In: 2D list containing all of the cards all of the players hold. Out: list containing the total value of all of those cards.  
This function simply takes all of the cards all players hold, and finds out their value. Aces are attributed a value of 11, as opposed to a soft/hard Ace that is normally used.

**playRound(game_id, roundID, players, account, cards)**
In: game_id, roundId, list of players, list of the amount of money each player has, deck of cards to use. Out: list of players, the updated amount of money they have, the list of the deck of cards after the round  
Main game playing function, explained in further detail below.

**gameStart(game_id, clientIDs)**
In: the ID of the game this will be, a list of players in the game. Out: void.  
This function is called by the matchmaking server, which provides the gameID and the clientIDs of the players in the game. This function sets everything up for the game, and then plays rounds of the game until only one player is left. At the end it writes out all of the packets sent and received to a file called (game_id).log

## playRound()

The playround function is the function in which most of the actual "blackjack" activity takes place. Initially, a reset packet is sent to each player, and a card is drawn (and then put back on the other side of the deck) for each player. This card is transmitted to all players. A card is similarly dealt for the dealer, and also sent to all players. A second card is dealt to each player, and transmitted to all players. The second card for the dealer is dealt, but NOT transmitted to any player.


Each player is then sent a request for a bet amount for the hand. If the player responds with a number that is greater than their current account balance, it is replaced by their current account balance. If the bet amount provided is less than or equal to 0, it will be replaced by half of their current account balance.  


From there, a request is sent to each player to find out whether they want to stand or hit. If they choose to hit, a card is dealt to them, and transmitted to all players. The total value of their cards are checked, and if it is over 21, they are eliminated. This procedure occurs for each player until all players either stand or are eliminated.  


Following this, the second card dealt to the dealer earlier is transmitted to all players, and the dealer will hit until it reaches a soft 17. Once that is reached (or the dealer goes bust), it is compared against the totals of all of the other players. If the dealer busts, all players who remain in are paid out their bet amount. If the player has a higher total than the dealer, the player is paid out their bet amount. If the player has a lower total than the dealer, the player loses their bet amount.
