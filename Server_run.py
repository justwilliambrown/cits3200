import ConnMan
import Blackjack_Server
import matchmaking_Server
import database

database.setup_db()
ConnMan.start()
matchmaking_Server.start()
