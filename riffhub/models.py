from datetime import datetime
from sqlalchemy import Time
from werkzeug.security import generate_password_hash, check_password_hash
from riffhub.extensions import db


# User Model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    events = db.relationship('Event', backref='organizer', lazy='dynamic', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    genres = db.relationship('Genre', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
        
    # Hash password for security
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    # Dehash password for verification
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


# Genre Model (moved up because Event references it)
class Genre(db.Model):
    __tablename__ = 'genres'


    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    events = db.relationship('Event', backref='genre', lazy='dynamic')
    
    def __repr__(self):
        return f'<Genre {self.title}>'


# Event Model
class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))    
    date = db.Column(db.Date, nullable=False)
    time = db.Column(Time, nullable=False)
    location = db.Column(db.String(120))
    image = db.Column(db.String(255))
    capacity = db.Column(db.Integer, default=0)  # 0 means unlimited capacity
    price = db.Column(db.Double, default=0)  # 0 means free entry
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tickets = db.relationship('Ticket', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    
    # Check tickets sold (excluding cancelled orders)
    @property
    def ticket_count(self):
        from riffhub.models import Order  # Import here to avoid circular imports
        
        return db.session.query(db.func.sum(Ticket.quantity))\
            .join(Order)\
            .filter(Ticket.event_id == self.id)\
            .filter(Order.status == 'completed')\
            .scalar() or 0
    
    # Check if event soldout
    @property
    def is_full(self):
        """Check if event has reached capacity"""
        return self.capacity > 0 and self.ticket_count >= self.capacity
    
    # Check tickets left to sell
    @property
    def available_tickets(self):
        """Number of tickets still available"""
        if self.capacity <= 0:  # Unlimited capacity
            return None
        return max(0, self.capacity - self.ticket_count)
        
    def __repr__(self):
        return f'<Event {self.title}>'


# Order Model
class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='completed')  # could be 'pending', 'completed', 'cancelled'
    
    # Relationships
    tickets = db.relationship('Ticket', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def total_tickets(self):
        """Total number of tickets in this order"""
        return sum(ticket.quantity for ticket in self.tickets)
    
    def __repr__(self):
        return f'<Order {self.id} by User {self.user_id}>'


# Ticket Model
class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Note: backref relationships are defined in Order and Event models
    
    def __repr__(self):
        return f'<Ticket {self.id}: {self.quantity} for Event {self.event_id}>'
    
# Comment Model
class Comment(db.Model):
    __tablename__ = 'comments'


    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    # Note: backref relationships are defined in User and Event models


    def __repr__(self):
        return f'<Comment {self.id}, by User {self.user_id} for Event {self.event_id}>'