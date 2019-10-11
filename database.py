import mysql.connector
import json

db = None

def setup_db():
	file = open("sqluser", 'r')
	userinfo = file.read()
	userdict = json.loads(userinfo)
	db = db = mysql.connector.connect(host='localhost', user=userdict['user'], password=userdict['password'])