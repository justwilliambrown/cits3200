Databse.py Documentation
======

## setup_db()
pulls the login information for the database, and creates the MySQL connection that the server uses. Expects no parameters, as details are listed in file on disk

## getMMR(ClientID)
used by the matchmaking server to obtain the users MMR rating for matchmaking purposes. ClientID is 

## updateMMR(ClientID, newMMR)
used to update the Client specified by the Client ID's MMR to the newMMR value

## getUsers(username)
Used by ConnMan to get the user, specified by that username, for login purposes
