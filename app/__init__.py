from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, ALL



app = Flask(__name__)
login = LoginManager(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
files = UploadSet('Files', extensions=('py','js','java','c','cpp'))
configure_uploads(app, files)

from app import routes, models
