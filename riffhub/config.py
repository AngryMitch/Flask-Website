import os
from datetime import timedelta

# Toggle for development environment.
# Set to True to use local SQLite DB, False to use production DB (e.g., on PythonAnywhere).
# IMPORTANT: Must always be False on the main branch for production deployment.
devEnv = True

# Get the absolute path to the current file's directory
basedir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(basedir, 'instance')

# Application configuration class
class Config:
    # Secret key used for securely signing the session cookie and CSRF tokens
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mitches_secret_key')

    # Create the instance directory if it doesn't already exist
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)

    # Set database URI based on the environment
    if devEnv is False:
        # Use environment variable or fallback to production path (PythonAnywhere)
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            'DATABASE_URL',
            f'sqlite:////home/angry0mitch/Flask-Website/instance/data.db'
        )
    else:
        # Use local SQLite database file in the instance directory
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(instance_dir, "data.db")}'

    # Disable SQLAlchemy modification tracking to reduce overhead
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Directory where uploaded files (e.g. images) will be stored
    UPLOAD_FOLDER = os.path.join('static', 'uploads')

    # Set of allowed file extensions for uploads
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # Max allowed file size for uploads (16 MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Set session lifetime to 1 hour
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
