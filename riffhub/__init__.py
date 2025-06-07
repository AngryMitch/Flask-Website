import os
from flask import Flask
from flask_bootstrap import Bootstrap
from riffhub.extensions import db, csrf
from riffhub.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)

    # Load configuration from the provided config class
    app.config.from_object(config_class)
    
    # Ensure the instance folder exists (used for DB, config, etc.)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Ensure the upload directory exists inside the static folder
    os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)
    
    # --- Register blueprints for modular routing ---
    # Main (public) routes
    from riffhub.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)

    # Authentication routes (login, register, etc.)
    from riffhub.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Event-related routes (create, view, edit events)
    from riffhub.blueprints.events import bp as events_bp
    app.register_blueprint(events_bp, url_prefix='/events')

    # --- Initialize Flask extensions ---
    db.init_app(app)    # Set up SQLAlchemy with the app
    csrf.init_app(app)  # Enable CSRF protection

    # --- Initialize the database if it doesn't exist ---
    with app.app_context():
        db.create_all()

    # --- Register context processors (template helpers) ---
    from riffhub.helpers import utility_processor
    app.context_processor(utility_processor)

    return app  # Return the configured app instance