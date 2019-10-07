import random
import ConnMan
import time
import matchmaking_Server



# cards: list simulating a deck of cards
# cardsHeld: 2D list containing the cards held by each player, [0] is the dealer.
# account: Dictionary for bank account containing the clientID as the key and money remaining as the value

# Receives JSON formatted packet from connection manager
# {"packet_type" : "GAME", "MOVE" : "HIT/STAND", "bet_amount": eg10, player_id : "fasd"}

loglist = []

playersEliminated = [] # This is a hack, but it works.

def disconnectHandle(playerid):
	global playersEliminated
	playersEliminated.append(playerid)

def receive(gameID, playerID):
	message = ConnMan.get_game_message(gameID)
	for i in range(5):
		if message != None:
			break
		time.sleep(1)
		message = ConnMan.get_game_message(gameID)
	loglist.append(str(message))

	try:
		if message["type"] == "CONTROL" and message["subtype"] == "DC":
			disconnectHandle(message["player_id"])
	except:
		pass

	while message["player_id"] != playerID:
		time.sleep(1)
		message = ConnMan.get_game_message(gameID)
		loglist.append(str(message))
	return message

def send(data):
	global playersEliminated
	if data["player_id"] in playersEliminated:
		return -1
	ConnMan.send_message(data["player_id"], data)
	loglist.append(str(data))
	print(data)
	return 0

def populateDeck(): #returns a shuffled deck of cards
	deck = []
	for i in ["H", "D", "C", "S"]:
		for j in range(2, 11):
			deck.append(str(j) + i)
		for j in ["J", "Q", "K", "A"]:
			deck.append(j + i)
	random.shuffle(deck)
	return deck

def calculateTotals(cardsHeld):
	totals = []
	for i in range(len(cardsHeld)):
		totals.append(0)
		for j in range(len(cardsHeld[i])):
			val = cardsHeld[i][j][0:-1]
			if val == "J" or val == "Q" or val == "K":
				totals[i] += 10
			elif val == "A":
				totals[i] += 11 # Aces are 11 sorry.
			else:
				totals[i] += int(val)
	return(totals)

def playRound(game_id, roundId, players, account, cards): # Game ID, ID of the round being played, the players in it, and their accounts left, the deck
	turnId = 0
	cardsHeld = [] # 2D list, [0] is dealer
	totals = [] # List of ints [0] is dealer
	bets = [0]

	global playersEliminated

	cardsHeld.append([])
	totals.append(0)

	cards.append(cards.pop(0)) # Burn the top card, and put it back on the bottom
	for i in range(1, len(players)): # Deal 1st card to each player
		send({"packet_type": "GAME", "type" : "RESET", "game_id" : game_id, "player_id":players[i]})
		cardsHeld.append([])
		curCard = cards.pop(0)
		cards.append(curCard) # Put the card back on bottom of the deck
		cardsHeld[i].append(curCard)
		send({"packet_type": "GAME", "type" : "BROADCAST", "game_id": game_id, "round_id":roundId, "turn_id":turnId, "player_id": players[i], "card" : curCard})

	dealCard1 = cards.pop(0)
	cardsHeld[0].append(dealCard1)
	cards.append(dealCard1)
	send({"packet_type": "GAME", "type" : "BROADCAST", "game_id": game_id, "round_id":roundId, "turn_id":turnId, "player_id": 0, "card" : dealCard1})


	for i in range(1, len(players)): # Deal 2nd card to each player
		cardsHeld.append([])
		curCard = cards.pop(0)
		cards.append(curCard) # Put the card back on bottom of the deck

		cardsHeld[i].append(curCard)
		send({"packet_type": "GAME", "type" : "BROADCAST", "game_id": game_id, "round_id":roundId, "turn_id":turnId, "player_id": players[i], "card" : curCard})


	dealCard1 = cards.pop(0)
	cards.append(dealCard1)
	cardsHeld[0].append(dealCard1)
	totals = calculateTotals(cardsHeld)

	for i in range(1, len(players)):
		# query the player for a bet amount
		if players[i] in playersEliminated:
			continue
		#send({"packet_type": "GAME", "type" : "RESET", "game_id" : game_id,"player_id":players[i]})
		print("Request bet from player_",players[i])

		while True:
			send({"packet_type" : "CONTROL", "type" : "REQUEST", "item" : "BETAMT", "player_id" : players[i]})
			message = receive(game_id, players[i])

			try:
				betAmount = message["BETAMT"]
			except:
				continue
			break

		if betAmount > account[players[i]]:
			betAmount = account[players[i]]
		if betAmount <= 0:
			betAmount = account[players[i]] / 2
		bets.append(betAmount)
	print(players[i]," bet ",betAmount)
	for i in range(1, len(players)): #Query each player for a move
		if players[i] in playersEliminated:
			continue
		turnId = 0
		# query the player
		#move = "" #TODO
		print("Player", players[i])
		while True:
			send({"packet_type" : "CONTROL", "type" : "REQUEST", "item" : "move", "player_id" : players[i]})
			message = receive(game_id, players[i])

			try:
				move = message["MOVE"]
			except:
				continue
			break

		turnId += 1
		while move != "STAND":
			print("REPEAT")

			print("Player", players[i], cardsHeld[i])
			if move == "HIT":
				#print(cards)
				curCard = cards.pop(0)
				cards.append(curCard)
				cardsHeld[i].append(curCard)
				send({"packet_type": "GAME", "type" : "BROADCAST", "game_id": game_id, "round_id":roundId, "turn_id":turnId, "player_id": players[i], "card" : curCard, "bet_amount" : bets[i]})
				totals = calculateTotals(cardsHeld)
				if totals[i] > 21:
					# Player is out
					send({"packet_type": "CONTROL", "type" : "BROADCAST", "move":"ELIMINATED", "player_id": players[i], "bet_amount":bets[i]}) # TODO
					account[players[i]] -= bets[i]
					break

				else :
					while True:
						send({"packet_type" : "CONTROL", "type" : "REQUEST", "item" : "move", "player_id" : players[i]})
						message = receive(game_id, players[i])
						try:
							move = message["MOVE"]
						except:
							continue
						break
				# Query player for input
				#move = input()
				turnId += 1

	# Send the dealer's second card
	send({"packet_type": "GAME", "type" : "BROADCAST", "game_id": game_id, "round_id":roundId, "turn_id":turnId, "player_id": 0, "card" : cardsHeld[0][1]})
	totals = calculateTotals(cardsHeld)

	# Dealer needs to hit until soft 17
	dealcount = 1
	while totals[0] < 17:
		dealcount += 1
		dealCard = cards.pop(0)
		cards.append(dealCard)
		cardsHeld[0].append(dealCard)
		send({"packet_type": "GAME", "type" : "BROADCAST", "game_id": game_id, "round_id":roundId, "turn_id":turnId, "player_id": 0, "card" : cardsHeld[0][dealcount]})
		totals = calculateTotals(cardsHeld)

	# Showdown
	for i in range(1, len(players)):
		if totals[i] > 21:
			continue
		elif totals[0] > 21: # Dealer busts, pay out
			send ({"packet_type": "CONTROL", "move":"WIN", "player_id":players[i]})
			account[players[i]] += bets[i]
		else:
			if totals[i] > totals[0]: # player wins
				send ({"packet_type": "CONTROL", "move":"WIN", "player_id":players[i]})
				account[players[i]] += bets[i]
			else:
				send ({"packet_type": "CONTROL", "move":"LOSS", "player_id":players[i]})
				account[players[i]] -= bets[i]

	return(players, account, cards)

def gameStart(game_id, clientIDs, tournamentMode):
	roundId = 0
	account = {} # Money in the client's account
	cards = []
	players = clientIDs
	players.insert(0, 0) # First item in players will be the dealer

	cards = populateDeck()

	for i in range(len(clientIDs)):
		account[clientIDs[i]] = 30 # 100 Starting balance for now

	while len(players) > 1:
		playersEliminated = []

		resultOfRound = playRound(game_id, roundId, players, account, cards)
		players = resultOfRound[0]
		account = resultOfRound[1]
		cards = resultOfRound[2]

		roundId += 1

		print("\n", account, "\n")
		for i in account:
			if account[i] <= 0:
				playersEliminated.append(i)
		for i in playersEliminated:
			players.remove(i)
			account.pop(i)

	# END OF GAME STUFF

	# Write to a file called (game_id).log
	filename = str(game_id) + ".log"
	logfile = open(filename, "w+")
	for message in loglist:
		logfile.write(message)
	logfile.close()
	if len(players) == 2: # One player wins
		matchmaking_Server.notifyFinish(game_id , players[1])
		if tournamentMode == True:
			send({"packet_type": "CONTROL", "type" : "LOBBY", "player_id" : players[1])
			for i in range(len(clientsIDs)):
				if clientIDs[i] != players[1]:
					send({"packet_type" : "CONTROL", "type" : "DC", "player_id" : players[i]})
		else:
			for i in range(len(clientsIDs)):
				send({"packet_type" : "CONTROL", "type" : "DC", "player_id" : players[i]})



#gameStart(1, [1,2,3])
