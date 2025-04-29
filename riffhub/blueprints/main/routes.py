# Main index page
from flask import render_template, request
from riffhub.blueprints.main import bp
from riffhub.models import Event
from datetime import datetime

@bp.route('/')
def index():
    """Homepage showing upcoming events"""
    events = Event.query.filter(Event.date >= datetime.now().date()).order_by(Event.date).all()
    return render_template('main/index.html', events=events)