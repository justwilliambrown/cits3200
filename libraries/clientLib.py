# Library to assist in interfacing clients with the server
# reformat(JSONstring) will take an encoded JSON string and format it as a Python Dictionary.
# format(Dictionary) will take a Python Dictionary and format it as an encoded JSON string.

# The idea behind this is that any message received over the connection can be put into the reformat
# function and you will get a python dictionary that you can use directly.
# Conversely, you can use the format function for any dictionary that you wish
# to send, and then directly send the result over the socket connection.
#
# Hopefully this will allow you to focus on the python side of this, without needing
# to deal with any JSON. Enjoy :)

# connect -> receive -> reformat
# format -> send

import json
import socket

def reformat(jstring): #Not to be confused with a gstring
    temp = jstring.decode()
    jdict = json.loads(temp)
    return jdict

def format(jdict): # IN: Dictionary. OUT: String
    jstring = json.dumps(jdict).encode()
    return jstring

def connect(addr, port): # In addres/port. OUT: socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = (addr, port)
    sock.connect(address)
    return(sock)

def receive(sock): #IN: Socket object. OUT: One (or more) messages received
    packet = sock.recv(4096)
    return packet

def send(sock, message):
    sock.send(message)
