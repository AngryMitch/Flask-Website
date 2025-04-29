# Authorisation Routes - Mithc
from flask import render_template, redirect, url_for, request, flash, session
from riffhub.blueprints.auth import bp
from riffhub.models import User, db

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
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
    
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.verify_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

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
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)