import mysql.connector
import json

db = None

def setup_db():
	file = open("sqluser", 'r')
	userinfo = file.read()
	userdict = json.loads(userinfo)
	db = db = mysql.connector.connect(host='localhost', user=userdict['user'], password=userdict['password'])
	file.close()

def getMMR(clientID):
    dbCursor = db.cursor(prepared=True)
    #TODO: Check that these are the column names in the database
    statement = "SELECT ranking FROM User Where id = %s"
    dbCursor.execute(query,clientID)
    if ranking in dbCursor:
        return ranking
    else:
        return -1

def updateMMR(clientID,newMMR):
    dbCursor = db.cursor(prepared = True)
    statement = "UPDATE user SET ranking = %s Where id = %s"
    data = (newMMR,clientID)
    dbCursor.execute(statement,data)
