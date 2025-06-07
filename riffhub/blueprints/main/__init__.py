# Main Render Page - mitch
from flask import Blueprint

# Create Blueprint
bp = Blueprint('main', __name__, template_folder='templates')

# Import routes
from riffhub.blueprints.main import routes