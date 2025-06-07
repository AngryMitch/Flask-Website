# Main index page
from flask import render_template, request
from data_generator import create_sample_data
from riffhub.blueprints.main import bp
from riffhub.models import Event, Genre
from datetime import datetime, date

@bp.route('/')
def index():
    """Homepage showing upcoming events"""
    today = datetime.now().date()  # Get today's date for filtering

    # Read selected genre ID from query string (e.g., ?genre=1)
    selected_genre = request.args.get('genre', type=int)

    # Query for events on or after today
    q = Event.query.filter(Event.date >= today)

    # Filter by genre if a genre was selected
    if selected_genre:
        q = q.filter_by(genre_id=selected_genre)

    # Retrieve and order the filtered events by date
    events = q.order_by(Event.date).all()

    # Retrieve all genres for the genre filter dropdown
    genres = Genre.query.order_by(Genre.title).all()

    # Render the homepage with events and genre options
    return render_template(
        'index.html',
        events=events,
        current_date=today,
        genres=genres,
        selected_genre=selected_genre
    )

@bp.route('/create-sample-data')
def create_sample_data_route():
    """Route to generate sample data (for development/testing)"""
    create_sample_data()
    return "Sample data created!"

# Error handler for 404 Not Found
@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Error handler for 500 Internal Server Error
@bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
