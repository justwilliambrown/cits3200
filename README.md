# CITS3200: Online Competitions for AI bots

**Team Members:** *Shu Zhou, William Chesnutt, Aidan Haile, Xiaojing Chen, ~~Jianwei Li~~, Benjamin Nguyen*


## Requirements

**1** Select a game for agents to compete in. (It could be very simple like
Rock-scissor paper, or one of the games we use in AAAI like The
Resistance, or Hanabi)
+ Blackjack

**2** Design a message passing interface for agents to play the game, where
messages are XML/JSON.

**3** Design and implement a socket API where agents can send and receive
the messages for the game.

**4** Design a tournament structure for agents to complete aginst one
another and accumulate a score or ranking.

**5** Design and implement a REST API for registering users and agents,
uploading agent source code, accessing activity logs of games played and
accessing the scoreboard/ranking.

**6** Queue System for starting games ie. once enough agents are ready then a game will start for those players

## JSON Formatting Information
{
  "packet_type" : type=string, // Describes the type of packet ("GAME" or "CONTROL")

  "game_id" : type=int, // ID of the game the packet is intended for

  "round_id" : type=int, // ID of the round of the game

  "turn_id" : type=int, // ID of the individual agent's turn in the game

  "player_id" : type=int, // ID of the agent/player

  "bet_amount" : type=int, // amount of money the agent chooses to bet

  "card" : type=string // The card dealt, formatted as "KC", "10D", etc...

}
