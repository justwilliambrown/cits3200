from flask import Flask, jsonify, loads, abort
from flask_restful import Api, Resource, fields, marshal
from os import listdir
import mysql.connector

app = Flask(__name__)
api = Api(app)

db = None

games_fields = {
	'Game_id' : fields.Integer,
	'URI' : fields.Url("game")
}

class GameListAPI(Resource):
	def get(self):
		#make a dictionary of the list of file names, minus the '.log' and converted into an integer, labeled with 'Game_id'
		games = [{"Game_id" : int(game[0:game.find('.log')])} for game in os.listdir()]
		return {'Games' : [marshal(game, games_fields) for game in games]}

class GameAPI(Resource):
	def get(self, Game_id):
		game = [game for game in listdir("gamelogs") if game == "{0}.log".format(Game_id)]

		if len(game) == 0:
			abort(404)

		jstring = ""
		with open(game[0]) as file:
			jstring = file.read()

		return flask.loads(jstring)


class leaderboardAPI(Resource):
	def get(self):
		cursor = db.cursor()
		cursor.exectute("SELECT username, ranking FROM app.users ORDER BY ranking DESC;")
		leaderboard = dict()
		for username, ranking in cursor:
			leaderboard[username] = ranking
		return leaderboard

api.add_resource(GameListAPI, '/api/1.0/games', endpoint='gamelist')
api.add_resource(GameAPI, '/api/1.0/games/<int:Game_id>', endpoint='game')
api.add_resource(leaderboardAPI, '/api/1.0/leaderboard', endpoint='leaderboard')

if __name__ == "__main__":
	file = open("sqluser", 'r')
	userinfo = file.read()
	userdict = json.loads(userinfo)
	db = db = mysql.connector.connect(host='localhost', user=userdict['user'], password=userdict['password'])
	app.run(debug=True)