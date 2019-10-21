import mysql.connector
import json
import threading

db = None
dbLock = threading.Lock()

def setup_db():
	global db
	file = open("sqluser.txt", 'r')
	userinfo = file.read()
	userdict = json.loads(userinfo)
	db = mysql.connector.connect(host='localhost', user="root", password="a",database='app')
	file.close()

def getMMR(clientID):
	global db
	dbLock.acquire()
	dbCursor = db.cursor(prepared=True)
	statement = "SELECT ranking,id FROM user Where id = %s"
	dbCursor.execute(statement,(clientID,))
	#TODO: Check values in dbCursor
	rank = -1
	#print("DBCURSOR: ",dbCursor)
	for (ranking,ID) in dbCursor:
		#print("RANKING: ",ranking)
		rank = ranking
	dbCursor.close()
	dbLock.release()
	return rank

def updateMMR(clientID,newMMR):
	dbLock.acquire()
	global db
	dbCursor = db.cursor(prepared = True)
	statement = "UPDATE user SET ranking = %s Where id = %s"
	#data = (newMMR,clientID)
	dbCursor.execute(statement,(newMMR,clientID))
	db.commit()
	dbLock.release()
	dbCursor.close()

def getUsers(username):
	dbLock.acquire()
	global db
	cursor = db.cursor(prepared=True)
	stmt = "select id, username, password_hash, ranking from user where username = %s"
	cursor.execute(stmt, (username,))
	retlist = []
	for (id, username, pHash, rank) in cursor:
		retlist.append((id, username, pHash, rank))

	cursor.close()
	dbLock.release()
	return retlist

def getDB():
	global db
	return db
