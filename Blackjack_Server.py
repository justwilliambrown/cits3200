import random

# cards: list simulating a deck of cards
# cardsHeld: 2D list containing the cards held by each player, [0] is the dealer.
# account: Dictionary for bank account containing the clientID as the key and money remaining as the value

# Receives JSON formatted packet from connection manager
clientIDs = ["1", "2", "3"] # For testing only
def receive():
	# TODO
	return 0

def send(data):
	# TODO
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

	cardsHeld.append([])
	totals.append(0)

	cards.append(cards.pop(0)) # Burn the top card, and put it back on the bottom
	for i in range(1, len(players)): # Deal 1st card to each player
		cardsHeld.append([])
		curCard = cards.pop(0)
		cards.append(curCard) # Put the card back on bottom of the deck
		cardsHeld[i].append(curCard)
		send({"packet_type": "GAME", "game_id": game_id, "round_id":roundId, "turn_id":turnId, "player_id": players[i], "card" : curCard})

	dealCard1 = cards.pop(0)
	cardsHeld[0].append(dealCard1)
	cards.append(dealCard1)
	send({"packet_type": "GAME", "game_id": game_id, "round_id":roundId, "turn_id":turnId, "player_id": 0, "card" : dealCard1})

	for i in range(1, len(players)): # Deal 2nd card to each player
		cardsHeld.append([])
		curCard = cards.pop(0)
		cards.append(curCard) # Put the card back on bottom of the deck

		cardsHeld[i].append(curCard)
		send({"packet_type": "GAME", "game_id": game_id, "round_id":roundId, "turn_id":turnId, "player_id": players[i], "card" : curCard})

	dealCard1 = cards.pop(0)
	cardsHeld[0].append(dealCard1)
	totals = calculateTotals(cardsHeld)

	for i in range(1, len(players)): #Query each player for a move
		turnId = 0
		# query the player
		#move = "" #TODO
		print("Player", players[i])
		move = input()
		turnId += 1
		while move != "STAND":
			print("Player", players[i], cardsHeld[i])
			if move == "HIT":
				#print(cards)
				curCard = cards.pop(0)
				cards.append(curCard)
				cardsHeld[i].append(curCard)
				send({"packet_type": "GAME", "game_id": game_id, "round_id":roundId, "turn_id":turnId, "player_id": players[i], "card" : curCard})
				totals = calculateTotals(cardsHeld)
				if totals[i] > 21:
					# Player is out
					send({"packet_type": "CONTROL", "move":"ELIMINATED", "player_id": players[i]}) # TODO
					print("Player", players[i], "eliminated", totals[i], cardsHeld[i])
					break
				# Query player for input
				move = input()
				turnId += 1
		# Send the dealer's second card
		send({"packet_type": "GAME", "game_id": game_id, "round_id":roundId, "turn_id":turnId, "player_id": 0, "card" : cardsHeld[0][1]})
		totals = calculateTotals(cardsHeld)

	# Dealer needs to hit until soft 17
	dealcount = 1
	while totals[0] < 17:
		dealcount += 1
		dealCard = cards.pop(0)
		cardsHeld[0].append(dealCard)
		send({"packet_type": "GAME", "game_id": game_id, "round_id":roundId, "turn_id":turnId, "player_id": 0, "card" : cardsHeld[0][dealcount]})
		totals = calculateTotals(cardsHeld)

	# Showdown
	for i in range(1, len(players)):
		if totals[i] > 21:
			break
		elif totals[0] > 21: # Dealer busts, pay out
			send ({"packet_type": "CONTROL", "move":"WIN", "player_id":players[i]})
		else:
			if totals[i] > totals[0]: # player wins
				send ({"packet_type": "CONTROL", "move":"WIN", "player_id":players[i]})
			else:
				send ({"packet_type": "CONTROL", "move":"LOSS", "player_id":players[i]})

	return(players, account, cards)

def gameStart(game_id, clientIDs):
	roundId = 0
	account = {} # Money in the client's account
	cards = []
	players = clientIDs
	players.insert(0, 0) # First item in players will be the dealer

	cards = populateDeck()

	for i in range(len(clientIDs)):
		account[clientIDs[i]] = 100 # 100 Starting balance for now

	while len(players) > 1:
		resultOfRound = playRound(game_id, roundId, players, account, cards)
		players = resultOfRound[0]
		account = resultOfRound[1]
		cards = resultOfRound[2]

		roundId += 1

		playersEliminated = []
		for i in account:
			if account[i] <= 0:
				playersEliminated.append(i)
		for i in playersEliminated:
			players.remove(i)
			account.remove(i)

gameStart(1, [1,2,3])
print(cards)
print(len(cards))
