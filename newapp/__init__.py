from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, ALL
from flask import Flask
from flask_admin import Admin
from flask_bootstrap import Bootstrap

from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length


from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView


# admin = Admin(app, template_mode = 'bootstrap3')
# admin.add_view(ModelView(User, db.session))
# admin.add_view(MyModelView(Game, db.session))
# admin.add_view(MyModelView(File, db.session))



app = Flask(__name__)
login = LoginManager(app)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
files = UploadSet('Files', extensions=('py','js','java','c','cpp'))
configure_uploads(app, files)


app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
admin = Admin(app, name='ai admin', template_mode='bootstrap3')
bootstrap = Bootstrap(app)
# admin.add_view(ModelView(User, db.session))

from app import routes, models
from app.models import User
admin.add_view(ModelView(User, db.session))



