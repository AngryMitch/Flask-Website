# Our Python Classes / Data Models - Mitch
from datetime import datetime
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
    events = db.relationship('Event', backref='organizer', lazy='dynamic')
    registrations = db.relationship('Registration', backref='user', lazy='dynamic')
    
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
    
    # Print statemen t
    def __repr__(self):
        return f'<User {self.username}>'

# Event Model
class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(20))
    location = db.Column(db.String(120))
    image = db.Column(db.String(255))
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    registrations = db.relationship('Registration', backref='event', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def registration_count(self):
        return self.registrations.count()
        
    def __repr__(self):
        return f'<Event {self.title}>'

# Registration Form Validation
class Registration(db.Model):
    __tablename__ = 'registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add unique constraint to prevent duplicate registrations
    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='_user_event_uc'),)
    
    def __repr__(self):
        return f'<Registration {self.user_id} for {self.event_id}>'