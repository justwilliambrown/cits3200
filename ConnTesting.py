import ConnMan
import queue

connMan = ConnMan.ConnMan()

print("starting ConnMan...")
connMan.start()
print("ConnMan started")
while True:
	message = connMan.get_message()
	if message == None:
		continue

	print("in server received message " +  message[1] + " from client " + message[0])
	print("echoing message back to client")
	connMan.send_message(message[0], message[1])