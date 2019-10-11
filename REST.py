from flask import Flask, jsonify, abort
from flask_restful import Api, Resource, fields, marshal

app = Flask(__name__)
api = Api(app)

games = [
	{
		'Game_id' : 1,
		'round_id' : 4
	},
	{
		'Game_id' : 2,
		'round_id' : '3'
	}
]

games_fields = {
	'Game_id' : fields.Integer,
	'URI' : fields.Url("game")
}

class GameListAPI(Resource):
	def get(self):
		return {'Games' : [marshal(game, games_fields) for game in games]}

class GameAPI(Resource):
	def get(self, Game_id):
		game = [game for game in games if game['Game_id'] == id]
		if len(game) == 0:
			abort(404)

		return {'game' : jsonify(game)}

api.add_resource(GameListAPI, '/api/1.0/games', endpoint='gamelist')
api.add_resource(GameAPI, '/api/1.0/game/<int:Game_id>', endpoint='game')

if __name__ == "__main__":
	app.run(debug=True)