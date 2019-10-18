from flask import Flask, jsonify, abort
from flask_restful import Api, Resource, fields, marshal
from os import listdir
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
		gamelogdir = os.getcwd()
		gamelogdir += "/gamelogs/"
		#make a dictionary of the list of file names, minus the '.log' and converted into an integer, labeled with 'Game_id'
		games = [{"Game_id" : float(game[0:game.find('.log')])} for game in os.listdir(gamelogdir)]
		return {'Games' : [marshal(game, games_fields) for game in games]}

class GameAPI(Resource):
	def get(self, Game_id):
		game = [game for game in listdir("gamelogs") if game == "{0}.log".format(Game_id)]

		if len(game) == 0:
			abort(404)

		jstring = ""
		with open(game[0]) as file:
			jstring = file.read()

		return json.loads(jstring)


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
api.add_resource(GameAPI, '/api/1.0/games/<int:Game_id>', endpoint='game')
api.add_resource(leaderboardAPI, '/api/1.0/leaderboard', endpoint='leaderboard')

def getDB():
        file = open("sqluser.txt", 'r')
        userinfo = file.read()
        userdict = json.loads(userinfo)
        db = mysql.connector.connect(host='localhost', user=userdict['user'], password=userdict['password'], database='app')
        return db

if __name__ == "__main__":
	app.run(debug=True)
