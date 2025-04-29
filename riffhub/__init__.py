import os
from flask import Flask
from riffhub.extensions import db
from riffhub.config import Config


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Ensure upload folder exists
    os.makedirs(os.path.join(app.static_folder, 'uploads'), exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints and extensions
    from riffhub.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from riffhub.blueprints.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from riffhub.blueprints.events import bp as events_bp
    app.register_blueprint(events_bp, url_prefix='/events')
    
    # Initialize database
    with app.app_context():
        db.create_all()
    
    # Context processors
    from riffhub.helpers import utility_processor
    app.context_processor(utility_processor)
    
    return app