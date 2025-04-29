# Account Management - mitch (copied and edited from main)
from flask import Blueprint

bp = Blueprint('events', __name__, template_folder='templates')

from riffhub.blueprints.events import routes