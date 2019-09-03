from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db,login
from hashlib import md5

#the tables of sql and related caculations are wirtten here 

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    ranking = db.Column(db.Integer)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    games = db.relationship('Game', backref='author', lazy='dynamic')
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def figure(self): 
        return 'https://bfgblog-a.akamaihd.net/uploads/2013/11/2-1-blackjack.png'
       

class Game(db.Model):
    Game_ID = db.Column(db.Integer, primary_key=True)
    Round_ID = db.Column(db.Integer)
    Turn_ID = db.Column(db.Integer)
    Card_ID = db.Column(db.Integer)
    Card_Total = db.Column(db.Integer)
    Number_of_Cards = db.Column(db.Integer)
    Money_Bet = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Game {}>'.format(self.body)




@login.user_loader
def load_user(id):
    return User.query.get(int(id))
