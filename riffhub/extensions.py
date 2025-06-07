from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# Create a SQLAlchemy database instance to be initialized with the Flask app
db = SQLAlchemy()

# Create a CSRFProtect instance to add CSRF protection to the app
csrf = CSRFProtect()