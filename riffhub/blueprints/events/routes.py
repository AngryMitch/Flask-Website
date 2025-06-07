from flask import render_template, redirect, url_for, request, flash, session, current_app
from riffhub.blueprints.events import bp
from riffhub.models import Event, Genre, Order, Ticket, User, Comment, db
from riffhub.helpers import login_required, save_image, utility_processor
from datetime import datetime, date
from sqlalchemy import func
from riffhub.forms import CancelTicketsForm, DeleteEventForm, EventForm, GenreForm, CommentForm, OrderTicketsForm

@bp.route('/')
def list():
    """List all upcoming events, optionally filtered by genre."""
    today = datetime.now().date()
    selected_genre = request.args.get('genre', type=int)

    # Query future events, filter by genre if selected
    q = Event.query.filter(Event.date >= today)
    if selected_genre:
        q = q.filter_by(genre_id=selected_genre)
    events = q.order_by(Event.date).all()

    # Load all genres for filter dropdown
    genres = Genre.query.order_by(Genre.title).all()

    return render_template('events.html',
                           events=events,
                           genres=genres,
                           selected_genre=selected_genre,
                           current_date=date.today())

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new event with form validation and image upload support."""
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            date=form.date.data,
            time=form.time.data,
            location=form.location.data,
            capacity=form.capacity.data or 0,
            price=form.price.data or 0,
            image=save_image(form.image.data) if form.image.data else None,
            organizer_id=session['user_id'],
            genre_id=form.genre.data.id if form.genre.data else None
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('events.detail', event_id=event.id))
    
    return render_template('create.html', form=form)

@bp.route('/<int:event_id>')
def detail(event_id):
    """Show event details, user ticket info, comments, and comment/delete forms."""
    event = Event.query.get_or_404(event_id)

    # Determine if current user has tickets for this event
    has_tickets = False
    ticket_count = 0
    if 'user_id' in session:
        user_tickets = Ticket.query.join(Order).filter(
            Order.user_id == session['user_id'],
            Ticket.event_id == event_id,
            Order.status == 'completed'
        ).all()
        has_tickets = bool(user_tickets)
        ticket_count = sum(ticket.quantity for ticket in user_tickets)
    
    # Load comments for the event
    comments = Comment.query.filter_by(event_id=event_id).order_by(Comment.created_at.desc()).all()
    
    # Prepare comment and delete forms if user is logged in and authorized
    comment_form = None
    delete_form = None
    if 'user_id' in session:
        comment_form = CommentForm()
        if event.organizer_id == session['user_id'] or session.get('is_admin', False):
            delete_form = DeleteEventForm()
    
    return render_template('detail.html',
                           event=event,
                           has_tickets=has_tickets,
                           ticket_count=ticket_count,
                           comments=comments,
                           comment_form=comment_form,
                           delete_form=delete_form,
                           current_date=date.today())

@bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    """Edit event details, image update allowed only for organizers/admins."""
    event = Event.query.get_or_404(event_id)

    # Permission check
    if event.organizer_id != session['user_id'] and not session.get('is_admin', False):
        flash('You do not have permission to edit this event', 'danger')
        return redirect(url_for('events.detail', event_id=event_id))

    form = EventForm(obj=event)

    if form.validate_on_submit():
        form.populate_obj(event)

        # Update image if a new one is uploaded
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
    """Delete event if user is organizer or admin."""
    event = Event.query.get_or_404(event_id)

    # Permission check
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
    """Allow users to order tickets for an event with capacity validation."""
    event = Event.query.get_or_404(event_id)
    
    # Determine max tickets available for purchase
    max_tickets = event.available_tickets if event.capacity > 0 else 100
    if max_tickets < 1:
        flash('No tickets available for this event.', 'danger')
        return redirect(url_for('events.detail', event_id=event.id))

    form = OrderTicketsForm(max_tickets=max_tickets)

    if form.validate_on_submit():
        quantity = form.quantity.data

        # Create new order and ticket records
        order = Order(user_id=session['user_id'])
        db.session.add(order)
        db.session.flush()  # Obtain order ID before adding ticket

        ticket = Ticket(order_id=order.id, event_id=event.id, quantity=quantity)
        db.session.add(ticket)
        db.session.commit()

        flash(f'Successfully ordered {quantity} ticket(s)!', 'success')
        return redirect(url_for('events.order_confirmation', order_id=order.id))

    return render_template('order_tickets.html', form=form, event=event)


@bp.route('/order/<int:order_id>/confirmation')
@login_required
def order_confirmation(order_id):
    """Show order confirmation page, ensuring user owns the order."""
    order = Order.query.get_or_404(order_id)

    # Verify order ownership
    if order.user_id != session['user_id']:
        flash('You do not have permission to view this order', 'danger')
        return redirect(url_for('events.list'))

    return render_template('order_confirmation.html',
                           order=order,
                           current_date=date.today())

@bp.route('/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_tickets(event_id):
    """Cancel all tickets for an event for the current user if event is upcoming."""
    # Fetch user's tickets for the event with completed orders
    tickets = Ticket.query.join(Order).filter(
        Order.user_id == session['user_id'],
        Ticket.event_id == event_id,
        Order.status == 'completed'
    ).all()

    if not tickets:
        flash('You have no tickets for this event', 'info')
        return redirect(url_for('events.detail', event_id=event_id))

    event = Event.query.get_or_404(event_id)

    # Prevent cancellation of past events
    if event.date < date.today():
        flash('Cannot cancel tickets for past events', 'warning')
        return redirect(url_for('events.detail', event_id=event_id))

    # Mark related orders as cancelled
    for ticket in tickets:
        ticket.order.status = 'cancelled'

    db.session.commit()
    flash('Your tickets have been cancelled', 'info')
    return redirect(url_for('events.my_tickets'))

@bp.route('/my-events')
@login_required
def my_events():
    """Show events created by the current logged-in user."""
    user_id = session['user_id']

    # Retrieve user's created events sorted by date
    created_events = Event.query.filter_by(organizer_id=user_id).order_by(Event.date).all()

    return render_template('my_events.html',
                           created_events=created_events,
                           current_date=date.today())

@bp.route('/my-tickets')
@login_required
def my_tickets():
    """Display all tickets and orders purchased by the current user."""
    user_id = session['user_id']

    # Get all orders made by user, newest first
    user_orders = Order.query.filter_by(user_id=user_id).order_by(Order.order_date.desc()).all()

    order_details = []
    cancel_forms = {}

    for order in user_orders:
        tickets_info = []
        for ticket in order.tickets:
            event = Event.query.get(ticket.event_id)
            tickets_info.append({'ticket': ticket, 'event': event})

            # Provide cancel form for future events with completed orders
            if event.date >= date.today() and order.status == 'completed':
                if event.id not in cancel_forms:
                    form = CancelTicketsForm()
                    form.event_id.data = event.id
                    cancel_forms[event.id] = form
        
        if tickets_info:
            order_details.append({'order': order, 'tickets': tickets_info})

    return render_template('my_tickets.html',
                           order_details=order_details,
                           cancel_forms=cancel_forms,
                           current_date=date.today())

@bp.route('/<int:event_id>/comment', methods=['POST'])
@login_required
def add_comment(event_id):
    """Add a comment to an event, validating non-empty input."""
    event = Event.query.get_or_404(event_id)
    form = CommentForm()
    if form.validate_on_submit():
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
    """Delete a comment if user owns it or is an admin."""
    comment = Comment.query.get_or_404(comment_id)
    event = Event.query.get_or_404(event_id)

    # Permission check for comment deletion
    if comment.user_id != session['user_id'] and not session.get('is_admin', False):
        flash('You do not have permission to delete this comment', 'danger')
        return redirect(url_for('events.detail', event_id=event_id))

    # Confirm comment belongs to this event
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
    """List existing genres and handle new genre creation with duplicate check."""
    form = GenreForm()
    genres = Genre.query.order_by(Genre.title).all()

    if form.validate_on_submit():
        name = form.name.data.strip()
        # Prevent duplicate genre titles
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
    """Render 404 page when resource is not found."""
    return render_template('404.html'), 404

@bp.app_errorhandler(500)
def internal_server_error(e):
    """Render 500 page for internal server errors."""
    return render_template('500.html'), 500
