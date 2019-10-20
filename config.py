import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{0}:3306/app'.format(os.environ.get('SQL_USER'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADED_FILES_DEST = os.getcwd()
    UPLOADED_FILES_ALLOW = ('py', 'java','js','c','cpp')
    LOG_FILES_DEST = os.getcwd()
