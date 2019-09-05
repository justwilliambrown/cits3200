import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(("127.0.0.1", 5051))
msg = {"type" : "test", "action" : "join"}
formatmsg = json.dumps(msg).encode()
sock.sendall(formatmsg)
reply = sock.recv(1024).decode()
print(reply)
sock.close()