import os
from datetime import timedelta

# TRUE = local db, FALSE = pythonanywhereDB. MUST ALWAYS BE FALSE in main branch
devEnv = True
basedir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(basedir, 'instance')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mitches_secret_key')

    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)

    if devEnv is False:
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            'DATABASE_URL',
            f'sqlite:////home/angry0mitch/Flask-Website/instance/data.db'
        )
    else:
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(instance_dir, "data.db")}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limit for file uploads
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)