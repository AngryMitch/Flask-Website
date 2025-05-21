from flask import render_template, redirect, url_for, request, flash, session, current_app
from riffhub.blueprints.events import bp
from riffhub.models import Event, Genre, Order, Ticket, User, Comment, db
# Import directly from helpers module
from riffhub.helpers import login_required, save_image, utility_processor
from datetime import datetime, date
from sqlalchemy import func
from riffhub.forms import EventForm, GenreForm, commentForm

@bp.route('/')
def list():
    """List all events"""
    today = datetime.now().date()
    # Read the selected genre from ?genre=<id>
    selected_genre = request.args.get('genre', type=int)
    # Base query for future events
    q = Event.query.filter(Event.date >= today)
    if selected_genre:
        q = q.filter_by(genre_id=selected_genre)
    events = q.order_by(Event.date).all()

    # Load genres to build dropdown
    genres = Genre.query.order_by(Genre.title).all()

    return render_template('events.html',
        events=events,
        genres=genres,
        selected_genre=selected_genre,
        current_date=today
    )

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new event"""
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title       = form.title.data,
            description = form.description.data,
            date        = form.date.data,
            time        = form.time.data,
            location    = form.location.data,
            capacity    = form.capacity.data or 0,
            image       = save_image(form.image.data) if form.image.data else None,
            organizer_id= session['user_id'],
            genre_id    = form.genre.data.id if form.genre.data else None
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('events.detail', event_id=event.id))
    
    return render_template('create.html', form=form)

@bp.route('/<int:event_id>')
def detail(event_id):
    """View event details"""
    event = Event.query.get_or_404(event_id)
    
    # Check if user has tickets for this event
    has_tickets = False
    ticket_count = 0
    if 'user_id' in session:
        # Get all tickets for this user and event
        user_tickets = Ticket.query.join(Order).filter(
            Order.user_id == session['user_id'],
            Ticket.event_id == event_id,
            Order.status == 'completed'
        ).all()
        
        has_tickets = len(user_tickets) > 0
        ticket_count = sum(ticket.quantity for ticket in user_tickets)
    
    # Get comments for this event
    comments = Comment.query.filter_by(event_id=event_id).order_by(Comment.created_at.desc()).all()
    
    # Create comment form if user is logged in
    comment_form = None
    if 'user_id' in session:
        comment_form = commentForm()
    
    # Format the date correctly for the template
    current_date = date.today()
    
    return render_template('detail.html', 
                          event=event, 
                          has_tickets=has_tickets,
                          ticket_count=ticket_count,
                          comments=comments,
                          comment_form=comment_form,
                          current_date=current_date)

@bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    """Edit an event"""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is the organizer
    if event.organizer_id != session['user_id'] and not session.get('is_admin', False):
        flash('You do not have permission to edit this event', 'danger')
        return redirect(url_for('events.detail', event_id=event_id))
    
    form = EventForm(obj=event)
    
    if form.validate_on_submit():
        form.populate_obj(event)
        
        # Save image if provided
        if form.image.data:
            image_filename = save_image(form.image.data)
            if image_filename:
                event.image = image_filename
        
        db.session.commit()
        flash('Event updated successfully!', 'success')
        return redirect(url_for('events.detail', event_id=event_id))
    
    return render_template('edit.html', form=form, event=event)

@bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete(event_id):
    """Delete an event"""
    event = Event.query.get_or_404(event_id)
    
    # Check if user is the organizer
    if event.organizer_id != session['user_id'] and not session.get('is_admin', False):
        flash('You do not have permission to delete this event', 'danger')
        return redirect(url_for('events.detail', event_id=event_id))
    
    db.session.delete(event)
    db.session.commit()
    
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('events.my_events'))

@bp.route('/<int:event_id>/order', methods=['GET', 'POST'])
@login_required
def order_tickets(event_id):
    """Order tickets for an event"""
    event = Event.query.get_or_404(event_id)
    
    # Check if event date is in the past
    if event.date < date.today():
        flash('This event has already occurred', 'warning')
        return redirect(url_for('events.detail', event_id=event_id))
    
    # Check if event is full
    if event.is_full:
        flash('This event is sold out', 'warning')
        return redirect(url_for('events.detail', event_id=event_id))
    
    if request.method == 'POST':
        # Get requested ticket quantity
        try:
            quantity = int(request.form.get('quantity', 1))
            if quantity <= 0:
                flash('Please select at least 1 ticket', 'danger')
                return redirect(url_for('events.order_tickets', event_id=event_id))
        except ValueError:
            flash('Invalid ticket quantity', 'danger')
            return redirect(url_for('events.order_tickets', event_id=event_id))
        
        # Check if enough tickets are available
        if event.capacity > 0 and (event.ticket_count + quantity > event.capacity):
            available = event.capacity - event.ticket_count
            if available <= 0:
                flash('This event is sold out', 'danger')
            else:
                flash(f'Only {available} tickets are available', 'danger')
            return redirect(url_for('events.detail', event_id=event_id))
        
        # Create order
        order = Order(user_id=session['user_id'])
        db.session.add(order)
        db.session.flush()  # Flush to get the order ID
        
        # Create ticket
        ticket = Ticket(
            order_id=order.id,
            event_id=event_id,
            quantity=quantity
        )
        db.session.add(ticket)
        db.session.commit()
        
        flash(f'Successfully ordered {quantity} ticket(s) for this event! Your order ID is #{order.id}', 'success')
        return redirect(url_for('events.my_tickets'))
    
    # GET request: show order form
    return render_template('order_tickets.html', event=event)

@bp.route('/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_tickets(event_id):
    """Cancel tickets for an event"""
    # Find user's tickets for this event
    tickets = Ticket.query.join(Order).filter(
        Order.user_id == session['user_id'],
        Ticket.event_id == event_id,
        Order.status == 'completed'
    ).all()
    
    if not tickets:
        flash('You have no tickets for this event', 'info')
        return redirect(url_for('events.detail', event_id=event_id))
    
    # Check if event has already occurred
    event = Event.query.get_or_404(event_id)
    if event.date < date.today():
        flash('Cannot cancel tickets for past events', 'warning')
        return redirect(url_for('events.detail', event_id=event_id))
    
    # Cancel the orders (set status to cancelled) 
    for ticket in tickets:
        ticket.order.status = 'cancelled'
    
    db.session.commit()
    flash('Your tickets have been cancelled', 'info')
    
    return redirect(url_for('events.my_tickets'))

@bp.route('/my-events')
@login_required
def my_events():
    """View events created by the current user"""
    user_id = session['user_id']
    
    # Events created by the user
    created_events = Event.query.filter_by(organizer_id=user_id).order_by(Event.date).all()
    
    # Current date for determining event status
    current_date = date.today()
    
    return render_template('my_events.html', 
                          created_events=created_events,
                          current_date=current_date)

@bp.route('/my-tickets')
@login_required
def my_tickets():
    """View tickets purchased by the current user"""
    user_id = session['user_id']
    
    # Get all orders for this user with their associated tickets and events
    user_orders = Order.query.filter_by(user_id=user_id).order_by(Order.order_date.desc()).all()
    
    order_details = []
    for order in user_orders:
        # Get all tickets for this order
        tickets_info = []
        for ticket in order.tickets:
            event = Event.query.get(ticket.event_id)
            tickets_info.append({
                'ticket': ticket,
                'event': event
            })
        
        if tickets_info:  # Only add orders that have tickets
            order_details.append({
                'order': order,
                'tickets': tickets_info
            })
    
    # Current date for determining ticket status
    current_date = date.today()
    
    return render_template('my_tickets.html', 
                          order_details=order_details,
                          current_date=current_date)

@bp.route('/<int:event_id>/comment', methods=['POST'])
@login_required
def add_comment(event_id):
    """Add a comment to an event"""
    event = Event.query.get_or_404(event_id)
    
    form = commentForm()
    if form.validate_on_submit():
        # Create new comment
        comment = Comment(
            user_id=session['user_id'],
            event_id=event_id,
            body=form.body.data
        )
        
        db.session.add(comment)
        db.session.commit()
        
        flash('Your comment has been posted', 'success')
    else:
        flash('Comment cannot be empty', 'danger')
    
    return redirect(url_for('events.detail', event_id=event_id))

@bp.route('/genres', methods=['GET', 'POST'])
@login_required
def genres():
    """List existing genres and allow creation of new ones."""
    form = GenreForm()
    genres = Genre.query.order_by(Genre.title).all()

    if form.validate_on_submit():
        name = form.name.data.strip()
        # Avoid duplicates
        if not Genre.query.filter_by(title=name).first():
            new_genre = Genre(title=name, user_id=session.get('user_id'))
            db.session.add(new_genre)
            db.session.commit()
            flash(f'Genre "{name}" added.', 'success')
        else:
            flash(f'Genre "{name}" already exists.', 'warning')
        return redirect(url_for('events.genres'))

    return render_template('genres.html',
                           form=form,
                           genres=genres)

# Error handlers
@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
