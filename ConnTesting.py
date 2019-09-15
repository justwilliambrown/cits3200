import ConnMan
import queue


print("starting ConnMan...")
ConnMan.start()
print("ConnMan started")
ConnMan.start_game(1)
while True:
	message = ConnMan.get_message(1)
	if message == None:
		continue

	print("in server received message {0} from client {1}", message[1], message[0])
	print("echoing message back to client")
	ConnMan.send_message(message[0], message[1])