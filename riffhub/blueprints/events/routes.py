from flask import render_template, redirect, url_for, request, flash, session, current_app
from riffhub.blueprints.events import bp
from riffhub.models import Event, Registration, User, db
from riffhub.helpers import login_required, save_image
from datetime import datetime

@bp.route('/')
def list():
    """List all events"""
    events = Event.query.order_by(Event.date).all()
    return render_template('index.html', events=events)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new event"""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        date_str = request.form['date']
        time = request.form['time']
        location = request.form['location']
        
        # Parse date
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'danger')
            return redirect(url_for('events.create'))
        
        # Save image if provided
        image_filename = None
        if 'image' in request.files:
            image_filename = save_image(request.files['image'])
        
        # Create event
        event = Event(
            title=title,
            description=description,
            date=date,
            time=time,
            location=location,
            image=image_filename,
            organizer_id=session['user_id']
        )
        
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully!', 'success')
        return redirect(url_for('events.detail', event_id=event.id))
    
    return render_template('create.html')

@bp.route('/<int:event_id>')
def detail(event_id):
    """View event details"""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is registered
    registered = False
    if 'user_id' in session:
        registration = Registration.query.filter_by(
            user_id=session['user_id'],
            event_id=event_id
        ).first()
        registered = registration is not None
    
    return render_template('detail.html', 
                          event=event, 
                          registered=registered)

@bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    """Edit an event"""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is the organizer
    if event.organizer_id != session['user_id']:
        flash('You do not have permission to edit this event', 'danger')
        return redirect(url_for('events.detail', event_id=event_id))
    
    if request.method == 'POST':
        event.title = request.form['title']
        event.description = request.form['description']
        
        # Parse date
        try:
            event.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'danger')
            return redirect(url_for('events.edit', event_id=event_id))
            
        event.time = request.form['time']
        event.location = request.form['location']
        
        # Save image if provided
        if 'image' in request.files and request.files['image'].filename:
            image_filename = save_image(request.files['image'])
            if image_filename:
                event.image = image_filename
        
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('events.detail', event_id=event_id))
    
    return render_template('edit.html', event=event)

@bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete(event_id):
    """Delete an event"""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is the organizer
    if event.organizer_id != session['user_id']:
        flash('You do not have permission to delete this event', 'danger')
        return redirect(url_for('events.detail', event_id=event_id))
    
    db.session.delete(event)
    db.session.commit()
    
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/<int:event_id>/register', methods=['POST'])
@login_required
def register(event_id):
    """Register for an event"""
    event = Event.query.get_or_404(event_id)
    
    # Check if already registered
    registration = Registration.query.filter_by(
        user_id=session['user_id'],
        event_id=event_id
    ).first()
    
    if registration:
        flash('You are already registered for this event', 'info')
    else:
        registration = Registration(
            user_id=session['user_id'],
            event_id=event_id
        )
        db.session.add(registration)
        db.session.commit()
        flash('Successfully registered for the event!', 'success')
    
    return redirect(url_for('events.detail', event_id=event_id))

@bp.route('/<int:event_id>/unregister', methods=['POST'])
@login_required
def unregister(event_id):
    """Unregister from an event"""
    registration = Registration.query.filter_by(
        user_id=session['user_id'],
        event_id=event_id
    ).first()
    
    if registration:
        db.session.delete(registration)
        db.session.commit()
        flash('You have unregistered from this event', 'info')
    
    return redirect(url_for('events.detail', event_id=event_id))

@bp.route('/my-events')
@login_required
def my_events():
    """View events created by the current user and events they are registered for"""
    user_id = session['user_id']
    
    # Events created by the user
    created_events = Event.query.filter_by(organizer_id=user_id).order_by(Event.date).all()
    
    # Events the user is registered for
    registered_events = Event.query.join(Registration).filter(Registration.user_id == user_id).order_by(Event.date).all()
    
    return render_template('my_events.html', 
                          created_events=created_events, 
                          registered_events=registered_events)