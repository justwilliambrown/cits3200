import random
import socket
from time import sleep
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 1234)
print ('connecting to %s port %s' % server_address)
sock.connect(server_address)

#Global Variables
clientID = '-1'
newPlayer = True
balance = 0
betPlace = False
cardTotal = 0

#Socket Loop
try:
    while True:
    
        exit = False
        # Request to join the server
        if(newPlayer):
            message = 'Request to join'.encode()
            print ('sending "%s"' % message)
            sock.send(message)
            newPlayer = False

        # Loop for packet reading
        amount_received = 0
        amount_expected = len(message)
        
        while amount_received < amount_expected:
            data = sock.recv(1024)
            amount_received += len(data)
            packet = data.decode()
            #Game_Start,%d,%d(clientID,Starting money)
            if "Game_Start" in packet:
                print("CLIENT_ID:",clientID)
                print("Packet Received:",packet)
                print("Game has been initialised\n")
                tempSplit = packet.split(",")
                for part in tempSplit:
                    if clientID in part:
                        continue
                    elif "Game_Start" in part:
                        continue
                    else:
                        balance = int(part.rstrip('\x00'))
                print("INITIAL balance ->",balance)
                sendMove = True
            #Connection_Success,%d (client_ID)
            if "Connection_Success" in packet:
                print("CLIENT_ID:",clientID)
                print("Packet Received:",packet)
                tempSplit = packet.split(",")
                clientID = tempSplit[1].rstrip('\x00')
                print("Client ID is:",clientID)
			#Round_Start,%d (clientID)
			if "Round_Start" in packet:
				print("Packet Received:", packet)
				print("Current balance", balance)
				#Check for bet amount input
				while True:
					try:
							betAmount = input("Please insert an amount to bet")
							if betAmount > balance or betAmount < 1:
								raise ErrorBet
							break
					except ErrorBet:
						print("Invalid value, must be > 1 and < Current Balance")
						print("Current Balance",balance)
			#Card_Start,%d,%d,%d(clientID,Card 1,Card 2)
			if "Card_Start" in packet:
				checkID = False
				print("Packet received:" packet)
				tempSplit = packet.split(",")
				for part in tempSplit:
					if "Card_Start" in part:
						continue
					else:
						if checkID == False:
							tempID = checkID.rstrip('\x00')
							if tempID == clientID:
								checkID = True
								continue
							else
								print("Received a different client's packet")
								checkID = True
								break
						#Read the Card ID and take action accordingly
						#TODO

			#Card_Dealt, %d,%d (ClientID, Card ID)
			if "Card_Dealt" in packet:
				checkID = False
				print("Packet received:" packet)
				tempSplit = packet.split(",")
				for part in tempSplit:
					if "Card_Dealt" in part:
						continue
					else:
						if checkID == False:
							tempID = checkID.rstrip('\x00')
							if tempID == clientID:
								checkID = True
								continue
							else
								print("Received a different client's packet")
								checkID = True
								break
						#Read the Card ID and take action accordingly
						#TODO
						
        if exit:
            print("Exit is true\n")
            break
finally:    
    print ('closing socket')
    sock.close()
