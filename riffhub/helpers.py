# Our general global helper functions - mitch
import os
from datetime import datetime
from functools import wraps
from flask import current_app, flash, redirect, url_for, session, request
from werkzeug.utils import secure_filename

# Allowed file types from ./config.py
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# Save the image to folder (defined in ./config.py)
def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to filename to avoid duplicates
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        new_filename = f"{timestamp}_{filename}"
        file.save(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], new_filename))
        return new_filename
    return None

# Block authorised pages if no user stored in session
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# This runs BEFORE the Jinja template is loaded. It's merged with the templates context
def utility_processor():
    def format_date(date_str):
        try:
            if isinstance(date_str, str):
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                return date_obj.strftime('%B %d, %Y')
            return date_str.strftime('%B %d, %Y')
        except:
            return date_str
            
    return dict(format_date=format_date, now=datetime.now())
