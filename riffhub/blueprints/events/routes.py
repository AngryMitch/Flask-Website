from flask import render_template, redirect, url_for, request, flash, session, current_app
from riffhub.blueprints.events import bp
from riffhub.models import Event, Genre, Order, Ticket, User, Comment, db
# Import directly from helpers module
from riffhub.helpers import login_required, save_image, utility_processor
from datetime import datetime, date
from sqlalchemy import func
from riffhub.forms import CancelTicketsForm, DeleteEventForm, EventForm, GenreForm, CommentForm, OrderTicketsForm

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
        current_date=date.today(),
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
            price       = form.price.data or 0,
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
        # Get all tickets for this user and event (excluding cancelled orders)
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
    delete_form = None
    if 'user_id' in session:
        comment_form = CommentForm()
        # Only create delete form if user is the organizer or admin
        if (event.organizer_id == session['user_id'] or session.get('is_admin', False)):
            delete_form = DeleteEventForm()
    
    # Format the date correctly for the template
    current_date = date.today()
    
    return render_template('detail.html', 
                          event=event, 
                          has_tickets=has_tickets,
                          ticket_count=ticket_count,
                          comments=comments,
                          comment_form=comment_form,
                          delete_form=delete_form,
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

@bp.route('/event/<int:event_id>/order', methods=['GET', 'POST'])
@login_required
def order_tickets(event_id):
    event = Event.query.get_or_404(event_id)
    
    max_tickets = event.available_tickets if event.capacity > 0 else 100
    if max_tickets < 1:
        flash('No tickets available for this event.', 'danger')
        return redirect(url_for('events.detail', event_id=event.id))

    form = OrderTicketsForm(max_tickets=max_tickets)

    if form.validate_on_submit():
        quantity = form.quantity.data

        # Create Order and Tickets
        order = Order(user_id=session['user_id'])
        db.session.add(order)
        db.session.flush()  # Get order.id before adding ticket

        ticket = Ticket(order_id=order.id, event_id=event.id, quantity=quantity)
        db.session.add(ticket)
        db.session.commit()

        flash(f'Successfully ordered {quantity} ticket(s)!', 'success')
        # Redirect to order confirmation page instead of my_tickets
        return redirect(url_for('events.order_confirmation', order_id=order.id))

    return render_template('order_tickets.html', form=form, event=event)


@bp.route('/order/<int:order_id>/confirmation')
@login_required
def order_confirmation(order_id):
    """Display order confirmation page"""
    order = Order.query.get_or_404(order_id)
    
    # Security check: ensure user owns this order
    if order.user_id != session['user_id']:
        flash('You do not have permission to view this order', 'danger')
        return redirect(url_for('events.list'))
    
    # Add current_date to template context
    current_date = date.today()
    
    return render_template('order_confirmation.html', 
                          order=order, 
                          current_date=current_date)

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
    cancel_forms = {}  # Dictionary to store forms by event_id
    
    for order in user_orders:
        # Get all tickets for this order
        tickets_info = []
        for ticket in order.tickets:
            event = Event.query.get(ticket.event_id)
            tickets_info.append({
                'ticket': ticket,
                'event': event
            })
            
            # Create cancel form for this event if it's in the future
            if event.date >= date.today() and order.status == 'completed':
                if event.id not in cancel_forms:
                    form = CancelTicketsForm()
                    form.event_id.data = event.id
                    cancel_forms[event.id] = form
        
        if tickets_info:  # Only add orders that have tickets
            order_details.append({
                'order': order,
                'tickets': tickets_info
            })
    
    # Current date for determining ticket status
    current_date = date.today()
    
    return render_template('my_tickets.html', 
                          order_details=order_details,
                          cancel_forms=cancel_forms,
                          current_date=current_date)

@bp.route('/<int:event_id>/comment', methods=['POST'])
@login_required
def add_comment(event_id):
    """Add a comment to an event"""
    event = Event.query.get_or_404(event_id)
    
    form = CommentForm()
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

@bp.route('/<int:event_id>/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(event_id, comment_id):
    """Delete a comment"""
    comment = Comment.query.get_or_404(comment_id)
    event = Event.query.get_or_404(event_id)
    
    # Check if user owns the comment or is admin
    if comment.user_id != session['user_id'] and not session.get('is_admin', False):
        flash('You do not have permission to delete this comment', 'danger')
        return redirect(url_for('events.detail', event_id=event_id))
    
    # Ensure comment belongs to this event
    if comment.event_id != event_id:
        flash('Comment not found for this event', 'danger')
        return redirect(url_for('events.detail', event_id=event_id))
    
    db.session.delete(comment)
    db.session.commit()
    
    flash('Comment deleted successfully', 'success')
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