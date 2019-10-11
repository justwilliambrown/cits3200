# Database

## User

Attributes|Data_tpye|Others
--|:--:|--:
id |Integer|primary_key
username |String(64)|index, unique
email |String(120)|index, unique
password_hash |String(128)
ranking |Integer

## Games

Attributes|Data_tpye|Others
--|:--:|--:
Game_ID |Integer|primary_key
Round_ID |Integer
Turn_ID |Integer
Card_ID |Integer
Card_Total|Integer
Money_Bet |Integer
timestamp |DateTime|index,default:datetime.utcnow
user_id |Integer|ForeignKey('user.id')

## Files

Attributes|Data_tpye|Others
--|:--:|--:
File_ID|Integer|primary_key
filename|String(64)|index, unique
timestamp |DateTime|index,default:datetime.utcnow
user_id |Integer|ForeignKey('user.id')

## package

python3 -m venv venv
virtualenv venv
venv/bin/activate

1. pip install (flask, python-dotenv,flask-wtf,flask-sqlalchemy,cryptography,pymysql,flask-migrate,flask-login,flask_uploads,flask_admin)
2. flask db init (app.db in you mysql)
3. flask db migrate -m "users table"
4. flask db upgrade
5. create upload_files
6. flask run

<a href="https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database">flask-db tutorial</a>
