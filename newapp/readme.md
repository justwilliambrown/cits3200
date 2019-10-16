bootstrap and flask admin installation guide


1. from flask_bootstrap import Bootstrap (bootstrap template)
entering the virtual environment and install (pip install -U Flask-WTF)

flask form:

from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length


2. from flask_admin import Admin
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView


{{ wtf.form_field(form.remember) }}