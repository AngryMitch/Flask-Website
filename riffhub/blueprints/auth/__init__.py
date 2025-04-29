# Main Render Page - mitch
from flask import Blueprint

bp = Blueprint('auth', __name__, template_folder='templates')

from riffhub.blueprints.auth import routes