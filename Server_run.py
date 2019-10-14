import ConnMan
import Blackjack_Server
import matchmaking_Server
import database

if __name__ == "__main__":
    database.setup_db()
    print("Database Initialised")
    ConnMan.start()
    print("Conn Man initialised")
    matchmaking_Server.start()
    print("Matchmaking Initialised")
