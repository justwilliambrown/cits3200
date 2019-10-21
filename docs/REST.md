REST api documentation
====

## Base URI's
Leaderboard URI: /api/1.0/leaderboard
Game list URI: /api/1.0/games
Specific game URI: /api/1.0/games/<game ID>

Implementation details
====

Each class represents a specific URI, and the get, post, etc. methods represent the HTTP packet type.
So, the GameListAPI represents the game list URI, the GameAPI works for the specific game, and the LeaderboardAPI deals with the leaderboard URI

Each URI is added for listening with the requisite api.add_resource line.
The same getDB function from connman is present as well.
