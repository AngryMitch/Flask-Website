from flask import render_template, redirect, url_for, flash, session
from riffhub.blueprints.auth import bp
from riffhub.forms import loginForm, registerForm
from riffhub.models import User, db

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    form = registerForm()
    



    
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
    form = loginForm()
    
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
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)