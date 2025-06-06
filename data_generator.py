#!/usr/bin/env python3
"""
RiffHub Sample Data Generator
This script creates sample data for the RiffHub application including:
- Admin user (login: admin, password: admin)
- Sample users
- Music genres
- Events
- Orders and tickets
- Comments

Usage:
1. Make sure your Flask app is set up and database is initialized
2. Run Flask app via python main.py
3. Go to http://127.0.0.1:5050/create-sample-data
"""

from datetime import datetime, date, time
from riffhub.extensions import db
from riffhub.models import User, Genre, Event, Order, Ticket, Comment

def create_sample_data():
    """Create all sample data for RiffHub"""
    
    print("Creating sample data for RiffHub...")
    
    # Clear existing data (optional - uncomment if you want to start fresh)
    #clear_all_data()
    
    # Create users
    users = create_sample_users()
    print(f"Created {len(users)} users")
    
    # Create genres
    genres = create_sample_genres(users)
    print(f"Created {len(genres)} genres")
    
    # Create events
    events = create_sample_events(users, genres)
    print(f"Created {len(events)} events")
    
    # Create orders and tickets
    orders = create_sample_orders(users, events)
    print(f"Created {len(orders)} orders")
    
    # Create comments
    comments = create_sample_comments(users, events)
    print(f"Created {len(comments)} comments")
    
    print("Sample data creation completed!")
    return users, genres, events, orders, comments

def clear_all_data():
    """Clear all existing data (use with caution!)"""
    print("Clearing existing data...")
    Comment.query.delete()
    Ticket.query.delete()
    Order.query.delete()
    Event.query.delete()
    Genre.query.delete()
    User.query.delete()
    db.session.commit()
    print("All data cleared!")

def create_sample_users():
    """Create sample users including admin"""
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@riffhub.com',
            'password': 'admin'
        },
        {
            'username': 'john_music',
            'email': 'john@example.com',
            'password': 'password123'
        },
        {
            'username': 'sarah_events',
            'email': 'sarah@example.com',
            'password': 'password123'
        },
        {
            'username': 'mike_rock',
            'email': 'mike@example.com',
            'password': 'password123'
        },
        {
            'username': 'emma_jazz',
            'email': 'emma@example.com',
            'password': 'password123'
        },
        {
            'username': 'alex_electronic',
            'email': 'alex@example.com',
            'password': 'password123'
        }
    ]
    
    users = []
    for user_data in users_data:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            user = User(
                username=user_data['username'],
                email=user_data['email']
            )
            user.password = user_data['password']
            db.session.add(user)
            users.append(user)
        else:
            users.append(existing_user)
    
    db.session.commit()
    return users

def create_sample_genres(users):
    """Create sample music genres"""
    genre_names = [
        'Rock', 'Jazz', 'Electronic', 'Pop', 'Hip Hop', 
        'Classical', 'Blues', 'Country', 'Reggae', 'Folk'
    ]
    
    genres = []
    for i, genre_name in enumerate(genre_names):
        # Check if genre already exists
        existing_genre = Genre.query.filter_by(title=genre_name).first()
        if not existing_genre:
            genre = Genre(
                title=genre_name,
                user_id=users[i % len(users)].id  # Distribute genres among users
            )
            db.session.add(genre)
            genres.append(genre)
        else:
            genres.append(existing_genre)
    
    db.session.commit()
    return genres

def create_sample_events(users, genres):
    """Create sample events with varying states"""
    events_data = [
        {
            'title': 'Summer Rock Festival',
            'description': 'The biggest rock festival of the year.',
            'date': date(2025, 7, 15),
            'time': time(18, 0),
            'location': 'Central Park Amphitheater',
            'capacity': 5000,
            'price': 75.00,
            'genre': 'Rock'
        },
        {
            'title': 'Past Jazz Night',
            'description': 'Jazz night already happened.',
            'date': date(2024, 12, 10),  # Past event
            'time': time(20, 0),
            'location': 'Blue Moon Jazz Club',
            'capacity': 150,
            'price': 35.00,
            'genre': 'Jazz'
        },
        {
            'title': 'Electronic Music Showcase',
            'description': 'Cutting-edge electronic artists.',
            'date': date(2025, 8, 5),
            'time': time(22, 0),
            'location': 'Tech Arena',
            'capacity': 0,  # Edge case: zero capacity
            'price': 45.00,
            'genre': 'Electronic'
        },
        {
            'title': 'Pop Stars Live',
            'description': 'Chart-toppers performing live.',
            'date': date(2025, 6, 30),
            'time': time(19, 30),
            'location': 'Stadium Arena',
            'capacity': 10000,
            'price': 85.00,
            'genre': 'Pop'
        },
        {
            'title': 'Sold Out Hip Hop Underground',
            'description': 'This event is sold out.',
            'date': date(2025, 7, 10),
            'time': time(21, 0),
            'location': 'Underground Club',
            'capacity': 2,  # Will simulate sold out by ticket orders
            'price': 25.00,
            'genre': 'Hip Hop'
        },
        {
            'title': 'Classical Symphony Evening',
            'description': 'Symphony by the city orchestra.',
            'date': date(2025, 9, 12),
            'time': time(19, 0),
            'location': 'Concert Hall',
            'capacity': 800,
            'price': 60.00,
            'genre': 'Classical'
        },
        {
            'title': 'Free Folk Concert',
            'description': 'Folk music for the community.',
            'date': date(2025, 6, 25),
            'time': time(17, 0),
            'location': 'Community Center',
            'capacity': 200,
            'price': 0.00,  # Free event
            'genre': 'Folk'
        },
        {
            'title': 'Past Blues & BBQ',
            'description': 'This blues fest is in the past.',
            'date': date(2024, 11, 5),  # Past event
            'time': time(16, 0),
            'location': 'Riverside Park',
            'capacity': 1500,
            'price': 40.00,
            'genre': 'Blues'
        }
    ]

    events = []
    for i, event_data in enumerate(events_data):
        genre = next((g for g in genres if g.title == event_data['genre']), genres[0])

        event = Event(
            title=event_data['title'],
            description=event_data['description'],
            genre_id=genre.id,
            date=event_data['date'],
            time=event_data['time'],
            location=event_data['location'],
            capacity=event_data['capacity'],
            price=event_data['price'],
            organizer_id=users[i % len(users)].id
        )
        db.session.add(event)
        events.append(event)

    db.session.commit()
    return events


def create_sample_orders(users, events):
    """Create sample orders and tickets"""
    orders_data = [
        # Valid upcoming events
        {'user_idx': 1, 'event_idx': 0, 'quantity': 2, 'status': 'completed'},  # Rock
        {'user_idx': 2, 'event_idx': 3, 'quantity': 1, 'status': 'completed'},  # Pop
        {'user_idx': 5, 'event_idx': 5, 'quantity': 3, 'status': 'completed'},  # Classical
        {'user_idx': 2, 'event_idx': 6, 'quantity': 5, 'status': 'completed'},  # Free event (Folk)

        # Sold out event (capacity = 2)
        {'user_idx': 4, 'event_idx': 4, 'quantity': 1, 'status': 'completed'},  # Hip Hop
        {'user_idx': 1, 'event_idx': 4, 'quantity': 1, 'status': 'completed'},  # Hip Hop

        # Past events
        {'user_idx': 3, 'event_idx': 1, 'quantity': 1, 'status': 'completed'},  # Past Jazz
        {'user_idx': 4, 'event_idx': 7, 'quantity': 2, 'status': 'completed'},  # Past Blues

        # Cancelled or pending
        {'user_idx': 5, 'event_idx': 3, 'quantity': 2, 'status': 'pending'},    # Pop
        {'user_idx': 3, 'event_idx': 6, 'quantity': 1, 'status': 'cancelled'}   # Free (Folk)
    ]

    orders = []
    for order_data in orders_data:
        if order_data['user_idx'] < len(users) and order_data['event_idx'] < len(events):
            event = events[order_data['event_idx']]
            # Skip if event has 0 capacity
            if event.capacity == 0:
                continue

            order = Order(
                user_id=users[order_data['user_idx']].id,
                status=order_data['status']
            )
            db.session.add(order)
            db.session.flush()  # Ensure order ID is available

            ticket = Ticket(
                order_id=order.id,
                event_id=event.id,
                quantity=order_data['quantity']
            )
            db.session.add(ticket)
            orders.append(order)

    db.session.commit()
    return orders


def create_sample_comments(users, events):
    """Create sample comments"""
    comments_data = [
        {'user_idx': 1, 'event_idx': 0, 'body': 'So excited for this rock festival! Going to be epic!'},
        {'user_idx': 2, 'event_idx': 1, 'body': 'Love jazz nights at Blue Moon. The atmosphere is always perfect.'},
        {'user_idx': 3, 'event_idx': 2, 'body': 'Electronic music showcase sounds amazing! Can\'t wait to experience it.'},
        {'user_idx': 4, 'event_idx': 3, 'body': 'Pop stars live is going to be incredible. Already got my tickets!'},
        {'user_idx': 5, 'event_idx': 4, 'body': 'Underground hip hop is where the real talent is. This will be fire!'},
        {'user_idx': 1, 'event_idx': 5, 'body': 'Classical music in a proper concert hall - pure magic.'},
        {'user_idx': 2, 'event_idx': 6, 'body': 'Love that this folk concert is free! Community events are the best.'},
        {'user_idx': 3, 'event_idx': 7, 'body': 'Blues and BBQ - perfect combination for a summer festival!'},
        {'user_idx': 4, 'event_idx': 0, 'body': 'Anyone know who the headlining bands are for the rock festival?'},
        {'user_idx': 5, 'event_idx': 1, 'body': 'Blue Moon has the best cocktails in town. Perfect for jazz night!'},
    ]
    
    comments = []
    for comment_data in comments_data:
        if comment_data['user_idx'] < len(users) and comment_data['event_idx'] < len(events):
            comment = Comment(
                user_id=users[comment_data['user_idx']].id,
                event_id=events[comment_data['event_idx']].id,
                body=comment_data['body']
            )
            db.session.add(comment)
            comments.append(comment)
    
    db.session.commit()
    return comments
