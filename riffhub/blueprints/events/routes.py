from flask import render_template, redirect, url_for, request, flash, session, current_app
from riffhub.blueprints.events import bp
from riffhub.models import Event, Genre, Order, Ticket, User, db
from riffhub.helpers import login_required, save_image
from datetime import datetime
from sqlalchemy import func
from riffhub.forms import EventForm, GenreForm  
@bp.route('/')
def list():
    """List all events"""
    today = datetime.now().date()
    # read the selected genre from ?genre=<id>
    selected_genre = request.args.get('genre', type=int)
    # base query for future events
    q = Event.query.filter(Event.date >= today)
    if selected_genre:
        q = q.filter_by(genre_id=selected_genre)
    events = q.order_by(Event.date).all()

    # load genres to build dropdown
    genres = Genre.query.order_by(Genre.title).all()

    return render_template('events.html',
        events=events,
        genres=genres,
        selected_genre=selected_genre
    )

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
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
        flash('Event created!', 'success')
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
    
    return render_template('detail.html', 
                          event=event, 
                          has_tickets=has_tickets,
                          ticket_count=ticket_count)

@bp.route('/<int:event_id>/edit', methods=['GET','POST'])
@login_required
def edit(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != session['user_id']:
        flash('No permission', 'danger')
        return redirect(url_for('events.detail', event_id=event.id))

    form = EventForm(obj=event)  # WTForms will call .populate_obj on the obj, including setting genre
    # Make sure the query_factory is still applied; no extra .choices setup needed

    if form.validate_on_submit():
        form.populate_obj(event)  # copies all fields, including `.genre` → `event.genre` via relationship
        db.session.commit()
        flash('Event updated!', 'success')
        return redirect(url_for('events.detail', event_id=event.id))

    return render_template('edit.html', form=form, event=event)

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

@bp.route('/<int:event_id>/order', methods=['GET', 'POST'])
@login_required
def order_tickets(event_id):
    """Order tickets for an event"""
    event = Event.query.get_or_404(event_id)
    
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
        
        # Create ticket
        ticket = Ticket(
            order_id=order.id,
            event_id=event_id,
            quantity=quantity
        )
        db.session.add(ticket)
        db.session.commit()
        
        flash(f'Successfully ordered {quantity} ticket(s) for this event!', 'success')
        return redirect(url_for('events.detail', event_id=event_id))
    
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
    
    # Cancel the orders (set status to cancelled) 
    for ticket in tickets:
        ticket.order.status = 'cancelled'
    
    db.session.commit()
    flash('Your tickets have been cancelled', 'info')
    
    return redirect(url_for('events.detail', event_id=event_id))

@bp.route('/my-events')
@login_required
def my_events():
    """View events created by the current user and events they have tickets for"""
    user_id = session['user_id']
    
    # Events created by the user
    created_events = Event.query.filter_by(organizer_id=user_id).order_by(Event.date).all()
    
    # Events the user has tickets for
    ticketed_events = Event.query.join(Ticket).join(Order).filter(
        Order.user_id == user_id,
        Order.status == 'completed'
    ).order_by(Event.date).all()
    
    # Get ticket counts for each event
    ticket_counts = {}
    for event in ticketed_events:
        # Get total quantity of tickets for this user and event
        quantity = db.session.query(func.sum(Ticket.quantity)).join(Order).filter(
            Order.user_id == user_id,
            Ticket.event_id == event.id,
            Order.status == 'completed'
        ).scalar() or 0
        ticket_counts[event.id] = quantity
    
    return render_template('my_events.html', 
                          created_events=created_events, 
                          ticketed_events=ticketed_events,
                          ticket_counts=ticket_counts)
    
    
@bp.route('/genres', methods=['GET', 'POST'])
def genres():
    """List existing genres and allow creation of new ones."""
    form = GenreForm()
    genres = Genre.query.order_by(Genre.title).all()

    if form.validate_on_submit():
        name = form.name.data.strip()
        # Avoid duplicates
        if not Genre.query.filter_by(title=name).first():
            new_genre = Genre(title=name, user_id=session.get('user_id') or None)
            db.session.add(new_genre)
            db.session.commit()
            flash(f'Genre "{name}" added.', 'success')
        else:
            flash(f'Genre "{name}" already exists.', 'warning')
        return redirect(url_for('events.genres'))

    return render_template('genres.html',
                           form=form,
                           genres=genres)