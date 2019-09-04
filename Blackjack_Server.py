import random

# Receives JSON formatted packet from connection manager
clientIDs = ["1", "2", "3"] # For testing only
def receive():
	# TODO
	return 0

def send(data):
	# TODO
	clientID = data[0]
	card = data[1]
	return 0

cards = []

def populateDeck(): #returns a shuffled deck of cards
	deck = []
	for i in ["H", "D", "C", "S"]:
		for j in range(2, 11):
			deck.append(str(j) + i)
		for j in ["J", "Q", "K", "A"]:
			deck.append(j + i)
	random.shuffle(deck)
	return deck

cards = populateDeck()
cardsHeld = [] # 2D list, [0] is dealer
totals = [] # List of ints [0] is dealer

def calculateTotals(clientNo):
	for i in cardsHeld[clientNo]:
		totals[clientNo] = 0
		val = i[0:-1]
		if val == "J" or val == "Q" or val == K:
			totals[clientNo] += 10
		elif val == "A":
			totals[clientNo] += 11
		else:
			totals[clientNo] += int(val)

def gameStart():
	cardsHeld.append([])
	totals.append(0)
	cards.pop(0) # Burn the top card
	for i in range(1, len(clientIDs)+1): # Deal 1st card to each player
		cardsHeld.append([])
		curCard = cards.pop(0)
		cardsHeld[i].append(curCard)
		send([i, curCard])

	dealCard1 = cards.pop(0)
	cardsHeld[0].append(dealCard1)
	send([dealCard1]) # TODO, get the formatting right

	for i in range(1, len(clientIDs)+1): # Deal 2nd card to each player
		cardsHeld.append([])
		curCard = cards.pop(0)
		cardsHeld[i].append(curCard)
		send([i, curCard])

	dealCard1 = cards.pop(0)
	cardsHeld[0].append(dealCard1)
	calculateTotals(0)

	for i in range(1, len(clientIDs)+1): #Query each player for a move
		totals.append(0)
		# Calculate totals
		calculateTotals(i)
		# query the player
		move = "" #TODO
		while move != "STAND":
			if move == "HIT":
				curCard = cards.pop(0)
				cardsHeld[i].append(curCard)
				send([i, curCard])
				calculateTotals(i)
				if totals[i] > 21:
					# Player is out
					send([i, "you're out"]) # TODO
					break
		# Send the dealer's second card
		send(cardsHeld[0][1]) #TODO
		calculateTotals(0)

	# Dealer needs to hit until soft 17
	while totals[0] < 17:
		dealCard = cards.pop(0)
		cardsHeld[0].append(dealCard)
		calculateTotals(0)

	# Showdown
	for i in range(1, len(clientIDs)+1):
		if totals[i] > 21:
			break
		elif totals[0] > 21: # Dealer busts, pay out
			send (["win"])
		else:
			if totals[i] > totals[0]: # player wins
				send ("win")
			else:
				send ("lose")

		

print(cards)
print(len(cards))