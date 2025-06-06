from flask import render_template, redirect, url_for, flash, session, request
from riffhub.blueprints.auth import bp
from riffhub.forms import LoginForm, RegisterForm, ProfileEditForm, ChangePasswordForm
from riffhub.models import User, Event, Order,db
from sqlalchemy import desc


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    form = RegisterForm()
    
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Check if username or email already exists
        user = User.query.filter((User.username == username) | (User.email == email)).first()
        if user:
            flash('Username or email already exists!', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create new user
        new_user = User(username=username, email=email)
        new_user.password = password  # This will hash the password
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.verify_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)


@bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))


@bp.route('/profile')
def profile():
    """User profile"""
    if 'user_id' not in session:
        flash('Please log in to access your profile', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(session['user_id'])
    
    # Get user statistics
    events_organized = user.events.count()
    total_tickets_sold = sum(event.ticket_count for event in user.events)
    
    # Get user's orders with event details
    orders = user.orders.order_by(desc(Order.order_date)).all()
    
    # Get user's genres
    genres = user.genres.all()
    
    # Get recent events organized by user
    recent_events = user.events.order_by(desc(Event.created_at)).limit(5).all()
    
    # Get recent comments by user
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
    """Edit user profile"""
    if 'user_id' not in session:
        flash('Please log in to access your profile', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(session['user_id'])
    form = ProfileEditForm(obj=user)
    
    if form.validate_on_submit():
        # Check if username or email is taken by another user
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data),
            User.id != user.id
        ).first()
        
        if existing_user:
            flash('Username or email already exists!', 'danger')
            return render_template('edit_profile.html', form=form, user=user)
        
        user.username = form.username.data
        user.email = form.email.data
        session['username'] = user.username  # Update session
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('edit_profile.html', form=form, user=user)


@bp.route('/profile/change-password', methods=['GET', 'POST'])
def change_password():
    """Change user password"""
    if 'user_id' not in session:
        flash('Please log in to access this page', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(session['user_id'])
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not user.verify_password(form.current_password.data):
            flash('Current password is incorrect', 'danger')
            return render_template('change_password.html', form=form)
        
        user.password = form.new_password.data
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('change_password.html', form=form)


@bp.route('/profile/delete-account', methods=['POST'])
def delete_account():
    """Delete user account"""
    if 'user_id' not in session:
        flash('Please log in to access this page', 'danger')
        return redirect(url_for('auth.login'))
    
    user = User.query.get_or_404(session['user_id'])
    
    try:
        # Clear the session first
        session.clear()
        
        # Delete the user (this will cascade delete related records)
        db.session.delete(user)
        db.session.commit()
        
        flash('Your account has been permanently deleted.', 'info')
        return redirect(url_for('main.index'))
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting your account. Please try again.', 'danger')
        return redirect(url_for('auth.profile'))


# Error handlers
@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
