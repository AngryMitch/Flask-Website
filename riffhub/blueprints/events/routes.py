from flask import render_template, redirect, url_for, request, flash, session, current_app
from riffhub.blueprints.events import bp
from riffhub.models import Event, Order, Ticket, User, db
from riffhub.helpers import login_required, save_image
from datetime import datetime
from sqlalchemy import func

@bp.route('/')
def list():
    """List all events"""
    events = Event.query.order_by(Event.date).all()
    return render_template('events.html', events=events)

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
        capacity = request.form.get('capacity', 0)
        try:
            capacity = int(capacity)
        except ValueError:
            capacity = 0
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'danger')
            return redirect(url_for('events.create'))
        
        image_filename = None
        if 'image' in request.files:
            image_filename = save_image(request.files['image'])
        
        event = Event(
            title=title,
            description=description,
            date=date_obj,
            time=time,
            location=location,
            capacity=capacity,
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
    has_tickets = False
    ticket_count = 0
    if 'user_id' in session:
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

@bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    """Edit an event"""
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != session['user_id']:
        flash('You do not have permission to edit this event', 'danger')
        return redirect(url_for('events.detail', event_id=event_id))
    
    if request.method == 'POST':
        event.title = request.form['title']
        event.description = request.form['description']
        try:
            event.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'danger')
            return redirect(url_for('events.edit', event_id=event_id))
        event.time = request.form['time']
        event.location = request.form['location']
        try:
            event.capacity = int(request.form.get('capacity', 0))
        except ValueError:
            flash('Invalid capacity value', 'danger')
            return redirect(url_for('events.edit', event_id=event_id))
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
    if event.date < date.today():
        flash('This event has already passed', 'danger')
        return redirect(url_for('events.detail', event_id=event_id))
    
    if request.method == 'POST':
        try:
            quantity = int(request.form.get('quantity', 1))
            if quantity <= 0:
                flash('Please select at least 1 ticket', 'danger')
                return redirect(url_for('events.order_tickets', event_id=event_id))
        except ValueError:
            flash('Invalid ticket quantity', 'danger')
            return redirect(url_for('events.order_tickets', event_id=event_id))
        
        if event.capacity > 0 and (event.ticket_count + quantity > event.capacity):
            available = event.capacity - event.ticket_count
            flash('This event is sold out' if available <= 0 else f'Only {available} tickets are available', 'danger')
            return redirect(url_for('events.detail', event_id=event_id))
        
        order = Order(user_id=session['user_id'])
        db.session.add(order)
        db.session.flush()
        ticket = Ticket(order_id=order.id, event_id=event_id, quantity=quantity)
        db.session.add(ticket)
        db.session.commit()
        
        flash(f'Successfully ordered {quantity} ticket(s) for this event! Your order ID is #{order.id}', 'success')
        return redirect(url_for('events.my_tickets'))
    
    return render_template('order_tickets.html', event=event)

@bp.route('/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel_tickets(event_id):
    """Cancel tickets for an event"""
    tickets = Ticket.query.join(Order).filter(
        Order.user_id == session['user_id'],
        Ticket.event_id == event_id,
        Order.status == 'completed'
    ).all()
    
    if not tickets:
        flash('You have no tickets for this event', 'info')
        return redirect(url_for('events.detail', event_id=event_id))

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
    current_date = date.today()
    created_events = Event.query.filter_by(organizer_id=user_id).order_by(Event.date).all()
    return render_template('my_events.html', created_events=created_events, current_date=current_date)

@bp.route('/my-tickets')
@login_required
def my_tickets():
    """View tickets purchased by the current user"""
    user_id = session['user_id']
    current_date = date.today()
    user_orders = Order.query.filter_by(user_id=user_id, status='completed').all()
    order_details = []

    for order in user_orders:
        order_info = {'order': order, 'tickets': []}
        for ticket in order.tickets:
            event = Event.query.get(ticket.event_id)
            if event:
                order_info['tickets'].append({'ticket': ticket, 'event': event})
        if order_info['tickets']:
            order_details.append(order_info)

    return render_template('my_tickets.html', order_details=order_details, current_date=current_date)
