# App Configuration -mitch
import os
from datetime import timedelta

# TRUE = local db, FALSE = pythonanywhereDB. MUST ALWAYS BE FALSE in main branch
devEnv = True
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mitches_secret_key')
    if(devEnv == False):
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            'DATABASE_URL',
            'sqlite:////home/angry0mitch/Flask-Website/instance/data.db'
        )
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limit for file uploads
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)