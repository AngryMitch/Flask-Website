from flask import render_template, redirect, url_for, flash, session, request
from riffhub.blueprints.auth import bp
from riffhub.forms import LoginForm, RegisterForm, ProfileEditForm, ChangePasswordForm
from riffhub.models import User, Event, Order, db
from sqlalchemy import desc


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Extract form data
        username = form.username.data
        email = form.email.data
        first_name = form.first_name.data
        surname = form.surname.data
        contact_number = form.contact_number.data
        street_address = form.street_address.data
        password = form.password.data
        
        # Check if username or email already exists
        user = User.query.filter((User.username == username) | (User.email == email)).first()
        if user:
            flash('Username or email already exists!', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create and save new user (password hashing handled in model setter)
        new_user = User(
            username=username, 
            email=email,
            first_name=first_name,
            surname=surname,
            contact_number=contact_number,
            street_address=street_address
        )
        new_user.password = password
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    # Show registration form
    return render_template('register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        
        # Verify user and password
        if user and user.verify_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))
        
        flash('Invalid username or password', 'danger')
    
    # Show login form
    return render_template('login.html', form=form)


@bp.route('/logout')
def logout():
    """User logout route - clears session"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))


@bp.route('/profile')
def profile():
    """User profile page with stats and recent activity"""
    if 'user_id' not in session:
        flash('Please log in to access your profile', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(session['user_id'])
    
    # Count events organized by user
    events_organized = user.events.count()
    # Sum tickets sold across user's events
    total_tickets_sold = sum(event.ticket_count for event in user.events)
    
    # Retrieve user's orders sorted by most recent
    orders = user.orders.order_by(desc(Order.order_date)).all()
    
    # User's favorite genres
    genres = user.genres.all()
    
    # Recent events organized (limit 5)
    recent_events = user.events.order_by(desc(Event.created_at)).limit(5).all()
    
    # Recent comments by user (limit 5)
    recent_comments = user.comments.order_by(desc('created_at')).limit(5).all()
    
    return render_template('profile.html', 
                           user=user,
                           events_organized=events_organized,
                           total_tickets_sold=total_tickets_sold,
                           orders=orders,
                           genres=genres,
                           recent_events=recent_events,
                           recent_comments=recent_comments)


@bp.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    """Edit user profile details"""
    if 'user_id' not in session:
        flash('Please log in to access your profile', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(session['user_id'])
    form = ProfileEditForm(obj=user)
    
    if form.validate_on_submit():
        # Prevent duplicate username/email for other users
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data),
            User.id != user.id
        ).first()
        
        if existing_user:
            flash('Username or email already exists!', 'danger')
            return render_template('edit_profile.html', form=form, user=user)
        
        # Update user fields
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.surname = form.surname.data
        user.contact_number = form.contact_number.data
        user.street_address = form.street_address.data
        session['username'] = user.username  # Keep session username updated
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    # Show profile edit form
    return render_template('edit_profile.html', form=form, user=user)


@bp.route('/profile/change-password', methods=['GET', 'POST'])
def change_password():
    """Change user password securely"""
    if 'user_id' not in session:
        flash('Please log in to access this page', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(session['user_id'])
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # Verify current password before changing
        if not user.verify_password(form.current_password.data):
            flash('Current password is incorrect', 'danger')
            return render_template('change_password.html', form=form)
        
        # Update to new password (hashing done in setter)
        user.password = form.new_password.data
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    # Show password change form
    return render_template('change_password.html', form=form)


@bp.route('/profile/delete-account', methods=['POST'])
def delete_account():
    """Delete user account and related data"""
    if 'user_id' not in session:
        flash('Please log in to access this page', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(session['user_id'])
    
    try:
        # Clear user session first
        session.clear()
        
        # Delete user record (cascades to related data)
        db.session.delete(user)
        db.session.commit()
        
        flash('Your account has been permanently deleted.', 'info')
        return redirect(url_for('main.index'))
        
    except Exception:
        db.session.rollback()
        flash('An error occurred while deleting your account. Please try again.', 'danger')
        return redirect(url_for('auth.profile'))


# Error handlers

@bp.app_errorhandler(404)
def page_not_found(e):
    """Render custom 404 page"""
    return render_template('404.html'), 404

@bp.app_errorhandler(500)
def internal_server_error(e):
    """Render custom 500 page"""
    return render_template('500.html'), 500
