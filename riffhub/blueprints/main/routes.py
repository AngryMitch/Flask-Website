# Main index page
from flask import render_template, request
from riffhub.blueprints.main import bp
from riffhub.models import Event
from datetime import datetime, date

@bp.route('/')
def index():
    """Homepage showing upcoming events"""
    events = Event.query.filter(Event.date >= datetime.now().date()).order_by(Event.date).all()
    return render_template('index.html', events=events, current_date=date.today())

# Error handlers
@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404