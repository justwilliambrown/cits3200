# Documentation giving an overview of the formatting of JSON packets

## Packets sent by Blackjack_Server.py

**Opening Balance packet, sent at game start:**
{"packet_type": "CONTROL", "game_id" : game_id, "type" : "OPENING_BALANCE", "player_id" : player_id, "BALANCE" : *opening balance for the game*}

**Reset packet, sent at round start:**
{"packet_type": "GAME", "type" : "RESET", "game_id" : game_id, "player_id":player_id}

**Card being dealt to a player:**
{"packet_type": "GAME", "type" : "BROADCAST", "game_id": game_id, "round_id":roundId, "turn_id":turnId, "player_id": *player receiving the card*, "card" : *card being dealt*}

**Card dealt to the dealer:**
{"packet_type": "GAME", "type" : "BROADCAST", "game_id": game_id, "round_id":roundId, "turn_id":turnId, "player_id": 0, "card" : *card dealt to the dealer*}

**Request to a player for the amount they wish to bet:**
{"packet_type" : "CONTROL", "type" : "REQUEST", "game_id": game_id, "item" : "BETAMT", "player_id" : player_id}

**Request to a player for a move:**
{"packet_type" : "CONTROL", "type" : "REQUEST", "game_id": game_id, "item" : "move", "player_id" : player_id}

**Player has won THAT HAND:**
{"packet_type": "CONTROL", "game_id": game_id, "move":"WIN", "player_id":player_id}

**Player has lost THAT HAND:**
{"packet_type": "CONTROL", "game_id": game_id, "move":"LOSS", "player_id":player_id}

**Player has busted in the hand:**
{"packet_type": "CONTROL", "type" : "BROADCAST", "move":"ELIMINATED", "game_id": game_id, "player_id": player_id, "bet_amount":*amount player bet on the hand*}

**Player has won a tournament game, and will be placed in the tournament lobby:**
{"packet_type": "CONTROL", "type" : "LOBBY", "player_id" : player_id}

**Player has won a Test Queue game:**
{"packet_type": "CONTROL", "game_id" : game_id, "type" : "VICTORY", "player_id" : player_id}

## Packets Sent by Blackjack_Client.py

**Login Details:**
{"user" : username, "pass" : password}

**Select which queue to join:**
{"Queue" : *which queue to join*, "player_id": player_id}

**Send the amount to bet on a particular hand:**
{"packet_type" : "CONTROL", "BETAMT" : *amount to bet*, "player_id" : player_id, "game_id": game_id}

**Send your move:**
{"packet_type" : "GAME", "MOVE": *move you wish to play*, "player_id" : client_id, "game_id" : game_id}

## ConnMan packets
**Initiate the login process, and request credentials**
{"packet_type" : "CONTROL", "subtype" : "loginRequest"}

**Lets the client know it's login was successful, and has joined the service, and informs client of their ID**
{"packet_type" : "CONTROL", "subtype" : "loginAccept", "id" : <id>}
  
**Informs the clien that their login has been denied, and will be disconnected**
{"packet_type" : "CONTROL", "subtype" : "loginDeny"}

**Informs the client that they are about to be disconnected from the service**
{"packet_type" : "CONTROL", "subtype" : "DC", "player_id" : <id>}
