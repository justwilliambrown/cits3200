from flask import Flask, jsonify, abort
from flask_restful import Api, Resource, fields, marshal
import os
import json
import mysql.connector

app = Flask(__name__)
api = Api(app)

db = None

games_fields = {
	'Game_id' : fields.Float,
	'URI' : fields.Url("game")
}

class GameListAPI(Resource):
	def get(self):
		print("got here")
		gamelogdir = os.getcwd()
		gamelogdir += "/gamelogs/"
		#make a dictionary of the list of file names, minus the '.log' and converted into an integer, labeled with 'Game_id'
		games = [{"Game_id" : float(game[0:game.find('.log')])} for game in os.listdir(gamelogdir)]
		return {'Games' : [marshal(game, games_fields) for game in games]}

class GameAPI(Resource):
	def get(self, Game_id):
		print("not a URI problem")
		gamelogdir = os.getcwd()
		gamelogdir += "/gamelogs"
		game = [game for game in os.listdir(gamelogdir) if game == "{0}.log".format(Game_id)]

		print(game)

		if len(game) == 0:
			abort(404)

		file = open(gamelogdir + "/" + game[0], "r")
		print("file is open")
		jstring = file.read()
		lines = jstring.split(";")

		retlist = []
		for line in lines:
			line = line.replace("\'", "\"")
			print(line)
			temp = json.loads(line)
			print("Succesfully loads")
			retlist.append(temp)

		print("it's a json error")
		return {Game_id : retlist}


class leaderboardAPI(Resource):
	def get(self):
            db = getDB()
            cursor = db.cursor()
            cursor.execute("select username, ranking from user order by ranking desc")
            leaderboard = dict()
            for (username, ranking) in cursor:
                print(username, ranking)
                leaderboard[username] = ranking
            cursor.close()
            db.close()
            return leaderboard

api.add_resource(GameListAPI, '/api/1.0/games', endpoint='gamelist')
api.add_resource(GameAPI, '/api/1.0/games/<float:Game_id>', endpoint='game')
api.add_resource(leaderboardAPI, '/api/1.0/leaderboard', endpoint='leaderboard')

def getDB():
        file = open("sqluser.txt", 'r')
        userinfo = file.read()
        userdict = json.loads(userinfo)
        db = mysql.connector.connect(host='localhost', user=userdict['user'], password=userdict['password'], database='app')
        return db

if __name__ == "__main__":
	app.run(debug=True)
