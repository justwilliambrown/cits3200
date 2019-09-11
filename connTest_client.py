import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(("127.0.0.1", 50519))
msg = {"type" : "test", "action" : "join"}
print(msg)
formatmsg = json.dumps(msg).encode()
print(formatmsg)
sock.sendall(formatmsg)
reply = sock.recv(1024).decode()
print("reply: ", reply)
print(reply)
sock.close()