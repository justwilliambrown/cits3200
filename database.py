import mysql.connector
import json

db = None

def setup_db():
	global db
	file = open("sqluser.txt", 'r')
	userinfo = file.read()
	userdict = json.loads(userinfo)
	db = mysql.connector.connect(host='localhost', user=userdict['user'], password=userdict['password'],database='app')
	file.close()

def getMMR(clientID):
	global db
	dbCursor = db.cursor(prepared=True)
	#TODO: Check that these are the column names in the database
	statement = "SELECT ranking,id FROM user Where id = %s"
	dbCursor.execute(statement,(clientID,))
	#TODO: Check values in dbCursor
	rank = -1
	print("DBCURSOR: ",dbCursor)
	for (ranking,ID) in dbCursor:
		print("RANKING: ",ranking)
		rank = ranking
	dbCursor.close()
	return rank

def updateMMR(clientID,newMMR):
	global db
	dbCursor = db.cursor(prepared = True)
	statement = "UPDATE user SET ranking = %s Where id = %s"
	#data = (newMMR,clientID)
	dbCursor.execute(statement,(newMMR,clientID))
	db.commit()
	dbCursor.close()

def getDB():
	global db
	return db
