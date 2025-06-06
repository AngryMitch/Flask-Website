# Main index page
from flask import render_template, request
from data_generator import create_sample_data
from riffhub.blueprints.main import bp
from riffhub.models import Event, Genre
from datetime import datetime, date

@bp.route('/')
def index():
    """Homepage showing upcoming events"""
    today = datetime.now().date()

    # Read the selected genre from ?genre=<id>
    selected_genre = request.args.get('genre', type=int)

    # Base query for future events
    q = Event.query.filter(Event.date >= today)

    # Apply genre filter if selected
    if selected_genre:
        q = q.filter_by(genre_id=selected_genre)

    # Finalize event query
    events = q.order_by(Event.date).all()

    # Load genres to build dropdown
    genres = Genre.query.order_by(Genre.title).all()

    return render_template(
        'index.html',
        events=events,
        current_date=today,
        genres=genres,
        selected_genre=selected_genre
    )

@bp.route('/create-sample-data')
def create_sample_data_route():
    create_sample_data()
    return "Sample data created!"

# Error handlers
@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404