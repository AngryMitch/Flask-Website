"""
RiffHub Sample Data Generator
This script creates sample data for the RiffHub application including:
- Admin user (login: admin, password: admin)
- Sample users with complete profile information
- Music genres
- Events with varied scenarios
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
    """Create sample users including admin with complete profile information"""
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@riffhub.com',
            'password': 'admin',
            'first_name': 'Admin',
            'surname': 'User',
            'contact_number': '+61 400 000 000',
            'street_address': '123 Admin Street, Brisbane, QLD 4000'
        },
        {
            'username': 'john_music',
            'email': 'john@example.com',
            'password': 'password123',
            'first_name': 'John',
            'surname': 'Smith',
            'contact_number': '+61 412 345 678',
            'street_address': '45 Music Lane, South Bank, QLD 4101'
        },
        {
            'username': 'sarah_events',
            'email': 'sarah@example.com',
            'password': 'password123',
            'first_name': 'Sarah',
            'surname': 'Johnson',
            'contact_number': '+61 423 456 789',
            'street_address': '78 Event Plaza, New Farm, QLD 4005'
        },
        {
            'username': 'mike_rock',
            'email': 'mike@example.com',
            'password': 'password123',
            'first_name': 'Mike',
            'surname': 'Williams',
            'contact_number': '+61 434 567 890',
            'street_address': '12 Rock Road, Fortitude Valley, QLD 4006'
        },
        {
            'username': 'emma_jazz',
            'email': 'emma@example.com',
            'password': 'password123',
            'first_name': 'Emma',
            'surname': 'Brown',
            'contact_number': '+61 445 678 901',
            'street_address': '33 Jazz Avenue, West End, QLD 4101'
        },
        {
            'username': 'alex_electronic',
            'email': 'alex@example.com',
            'password': 'password123',
            'first_name': 'Alex',
            'surname': 'Davis',
            'contact_number': '+61 456 789 012',
            'street_address': '56 Electronic Circuit, Kangaroo Point, QLD 4169'
        },
        {
            'username': 'lisa_pop',
            'email': 'lisa@example.com',
            'password': 'password123',
            'first_name': 'Lisa',
            'surname': 'Wilson',
            'contact_number': '+61 467 890 123',
            'street_address': '89 Pop Street, Paddington, QLD 4064'
        },
        {
            'username': 'david_classical',
            'email': 'david@example.com',
            'password': 'password123',
            'first_name': 'David',
            'surname': 'Miller',
            'contact_number': '+61 478 901 234',
            'street_address': '21 Symphony Street, Toowong, QLD 4066'
        },
        {
            'username': 'anna_folk',
            'email': 'anna@example.com',
            'password': 'password123',
            'first_name': 'Anna',
            'surname': 'Taylor',
            'contact_number': '+61 489 012 345',
            'street_address': '67 Folk Lane, Milton, QLD 4064'
        },
        {
            'username': 'chris_blues',
            'email': 'chris@example.com',
            'password': 'password123',
            'first_name': 'Chris',
            'surname': 'Anderson',
            'contact_number': '+61 490 123 456',
            'street_address': '34 Blues Boulevard, Woolloongabba, QLD 4102'
        },
        {
            'username': 'jessica_country',
            'email': 'jessica@example.com',
            'password': 'password123',
            'first_name': 'Jessica',
            'surname': 'Martinez',
            'contact_number': '+61 401 234 567',
            'street_address': '90 Country Road, Auchenflower, QLD 4066'
        },
        {
            'username': 'ryan_hiphop',
            'email': 'ryan@example.com',
            'password': 'password123',
            'first_name': 'Ryan',
            'surname': 'Garcia',
            'contact_number': '+61 402 345 678',
            'street_address': '15 Hip Hop Street, Teneriffe, QLD 4005'
        }
    ]
    
    users = []
    for user_data in users_data:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                surname=user_data['surname'],
                contact_number=user_data['contact_number'],
                street_address=user_data['street_address']
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
        'Classical', 'Blues', 'Country', 'Reggae', 'Folk',
        'Metal', 'Indie', 'R&B', 'Punk', 'Alternative'
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
    """Create sample events with varying states and scenarios"""
    events_data = [
        # Upcoming events
        {
            'title': 'Summer Rock Festival 2025',
            'description': 'The biggest rock festival of the year featuring international and local bands. Three stages, food trucks, and camping available.',
            'date': date(2025, 8, 15),
            'time': time(14, 0),
            'location': 'Riverstage, South Bank, Brisbane',
            'capacity': 8000,
            'price': 89.50,
            'genre': 'Rock',
        },
        {
            'title': 'Electronic Music Showcase',
            'description': 'Cutting-edge electronic artists from around the world. Mind-bending visuals and sound.',
            'date': date(2025, 7, 20),
            'time': time(20, 0),
            'location': 'The Tivoli, Fortitude Valley',
            'capacity': 1500,
            'price': 65.00,
            'genre': 'Electronic',
        },
        {
            'title': 'Pop Stars Live Concert',
            'description': 'Chart-toppers performing their biggest hits live. Special guest appearances expected.',
            'date': date(2025, 9, 5),
            'time': time(19, 30),
            'location': 'Brisbane Entertainment Centre',
            'capacity': 12000,
            'price': 95.00,
            'genre': 'Pop',
        },
        {
            'title': 'Intimate Jazz Evening',
            'description': 'An intimate evening of smooth jazz with Brisbane\'s finest musicians.',
            'date': date(2025, 6, 25),
            'time': time(19, 0),
            'location': 'Brisbane Jazz Club, Kangaroo Point',
            'capacity': 120,
            'price': 45.00,
            'genre': 'Jazz',
        },
        {
            'title': 'Hip Hop Underground',
            'description': 'Raw, authentic hip hop in an underground setting. Local talent showcase.',
            'date': date(2025, 7, 8),
            'time': time(21, 0),
            'location': 'The Foundry, Fortitude Valley',
            'capacity': 200,
            'price': 35.00,
            'genre': 'Hip Hop',
        },
        {
            'title': 'Classical Symphony Gala',
            'description': 'Queensland Symphony Orchestra presents a night of classical masterpieces.',
            'date': date(2025, 8, 30),
            'time': time(19, 30),
            'location': 'QPAC Concert Hall, South Bank',
            'capacity': 1800,
            'price': 85.00,
            'genre': 'Classical',
        },
        {
            'title': 'Free Folk Festival',
            'description': 'Community folk music festival featuring local artists. Family-friendly event.',
            'date': date(2025, 6, 30),
            'time': time(15, 0),
            'location': 'New Farm Park, Brisbane',
            'capacity': 2000,
            'price': 0.00,
            'genre': 'Folk',
        },
        {
            'title': 'Blues & BBQ Festival',
            'description': 'Authentic blues music paired with delicious BBQ. Perfect weekend combo.',
            'date': date(2025, 9, 20),
            'time': time(12, 0),
            'location': 'Roma Street Parkland',
            'capacity': 3000,
            'price': 55.00,
            'genre': 'Blues',
        },
        {
            'title': 'Country Music Jamboree',
            'description': 'Traditional and modern country music celebration with line dancing.',
            'date': date(2025, 10, 15),
            'time': time(18, 0),
            'location': 'RNA Showgrounds, Bowen Hills',
            'capacity': 5000,
            'price': 70.00,
            'genre': 'Country',
        },
        {
            'title': 'Reggae Sunset Sessions',
            'description': 'Chill reggae vibes as the sun sets over the Brisbane River.',
            'date': date(2025, 7, 12),
            'time': time(17, 0),
            'location': 'Howard Smith Wharves',
            'capacity': 800,
            'price': 40.00,
            'genre': 'Reggae',
        },
        {
            'title': 'Metal Mayhem',
            'description': 'Heavy metal showcase featuring brutal riffs and thunderous drums.',
            'date': date(2025, 8, 3),
            'time': time(19, 0),
            'location': 'The Triffid, Newstead',
            'capacity': 600,
            'price': 50.00,
            'genre': 'Metal',
        },
        {
            'title': 'Indie Music Discovery',
            'description': 'Discover the next big indie acts before they hit the mainstream.',
            'date': date(2025, 6, 20),
            'time': time(20, 0),
            'location': 'The Zoo, Fortitude Valley',
            'capacity': 350,
            'price': 30.00,
            'genre': 'Indie',
        },
        {
            'title': 'R&B Soul Night',
            'description': 'Smooth R&B and soul music to soothe your soul and move your body.',
            'date': date(2025, 9, 10),
            'time': time(20, 30),
            'location': 'Princess Theatre, Woolloongabba',
            'capacity': 900,
            'price': 60.00,
            'genre': 'R&B',
        },
        {
            'title': 'Punk Rock Rebellion',
            'description': 'Fast, loud, and rebellious. Classic punk rock attitude and energy.',
            'date': date(2025, 7, 25),
            'time': time(21, 30),
            'location': 'Crowbar, Fortitude Valley',
            'capacity': 250,
            'price': 25.00,
            'genre': 'Punk',
        },
        {
            'title': 'Alternative Rock Fest',
            'description': 'Alternative rock bands pushing boundaries and creating unique sounds.',
            'date': date(2025, 8, 8),
            'time': time(18, 30),
            'location': 'Eatons Hill Outdoors',
            'capacity': 4000,
            'price': 75.00,
            'genre': 'Alternative',
        },
        # Past events for testing
        {
            'title': 'Jazz Night at Blue Moon',
            'description': 'Intimate jazz performance that already happened.',
            'date': date(2024, 12, 15),
            'time': time(20, 0),
            'location': 'Blue Moon Jazz Club',
            'capacity': 100,
            'price': 35.00,
            'genre': 'Jazz',
        },
        {
            'title': 'Rock Concert Last Year',
            'description': 'Amazing rock concert from last year.',
            'date': date(2024, 11, 20),
            'time': time(19, 0),
            'location': 'Riverstage',
            'capacity': 6000,
            'price': 80.00,
            'genre': 'Rock',
        },
        # Event with unlimited capacity
        {
            'title': 'Virtual Electronic Experience',
            'description': 'Unlimited capacity virtual reality electronic music experience.',
            'date': date(2025, 10, 31),
            'time': time(20, 0),
            'location': 'Virtual Reality Venue',
            'capacity': 0,  # Unlimited capacity
            'price': 25.00,
            'genre': 'Electronic',
        },
        # Small capacity event for testing sold out scenario
        {
            'title': 'Exclusive Acoustic Session',
            'description': 'Very intimate acoustic session with limited seating.',
            'date': date(2025, 6, 15),
            'time': time(19, 0),
            'location': 'Private Studio, Brisbane',
            'capacity': 5,  # Very small capacity
            'price': 100.00,
            'genre': 'Folk',
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
            image=event_data.get('image'),
            capacity=event_data['capacity'],
            price=event_data['price'],
            organizer_id=users[i % len(users)].id
        )
        db.session.add(event)
        events.append(event)

    db.session.commit()
    return events

def create_sample_orders(users, events):
    """Create sample orders and tickets with various scenarios"""
    orders_data = [
        # Regular orders for upcoming events
        {'user_idx': 1, 'event_idx': 0, 'quantity': 2, 'status': 'completed'},  # Rock Festival
        {'user_idx': 2, 'event_idx': 1, 'quantity': 1, 'status': 'completed'},  # Electronic
        {'user_idx': 3, 'event_idx': 2, 'quantity': 3, 'status': 'completed'},  # Pop
        {'user_idx': 4, 'event_idx': 3, 'quantity': 2, 'status': 'completed'},  # Jazz
        {'user_idx': 5, 'event_idx': 4, 'quantity': 1, 'status': 'completed'},  # Hip Hop
        {'user_idx': 6, 'event_idx': 5, 'quantity': 4, 'status': 'completed'},  # Classical
        {'user_idx': 7, 'event_idx': 6, 'quantity': 6, 'status': 'completed'},  # Free Folk
        {'user_idx': 8, 'event_idx': 7, 'quantity': 2, 'status': 'completed'},  # Blues
        {'user_idx': 9, 'event_idx': 8, 'quantity': 1, 'status': 'completed'},  # Country
        {'user_idx': 10, 'event_idx': 9, 'quantity': 2, 'status': 'completed'}, # Reggae
        {'user_idx': 11, 'event_idx': 10, 'quantity': 1, 'status': 'completed'}, # Metal
        {'user_idx': 1, 'event_idx': 11, 'quantity': 2, 'status': 'completed'}, # Indie
        {'user_idx': 2, 'event_idx': 12, 'quantity': 1, 'status': 'completed'}, # R&B
        {'user_idx': 3, 'event_idx': 13, 'quantity': 3, 'status': 'completed'}, # Punk
        {'user_idx': 4, 'event_idx': 14, 'quantity': 2, 'status': 'completed'}, # Alternative
        
        # Past event orders
        {'user_idx': 5, 'event_idx': 15, 'quantity': 1, 'status': 'completed'}, # Past Jazz
        {'user_idx': 6, 'event_idx': 16, 'quantity': 2, 'status': 'completed'}, # Past Rock
        
        # Virtual event (unlimited capacity)
        {'user_idx': 7, 'event_idx': 17, 'quantity': 1, 'status': 'completed'}, # Virtual
        
        # Fill up the small capacity event to make it sold out
        {'user_idx': 8, 'event_idx': 18, 'quantity': 2, 'status': 'completed'}, # Acoustic
        {'user_idx': 9, 'event_idx': 18, 'quantity': 2, 'status': 'completed'}, # Acoustic
        {'user_idx': 10, 'event_idx': 18, 'quantity': 1, 'status': 'completed'}, # Acoustic (should be sold out now)
        
        # Pending and cancelled orders
        {'user_idx': 11, 'event_idx': 0, 'quantity': 1, 'status': 'pending'},    # Rock Festival
        {'user_idx': 1, 'event_idx': 2, 'quantity': 2, 'status': 'cancelled'},  # Pop
        {'user_idx': 2, 'event_idx': 6, 'quantity': 1, 'status': 'cancelled'},  # Free Folk
        
        # More orders to create realistic data
        {'user_idx': 3, 'event_idx': 1, 'quantity': 1, 'status': 'completed'}, # Electronic
        {'user_idx': 4, 'event_idx': 0, 'quantity': 1, 'status': 'completed'}, # Rock Festival
        {'user_idx': 5, 'event_idx': 7, 'quantity': 1, 'status': 'completed'}, # Blues
        {'user_idx': 6, 'event_idx': 9, 'quantity': 1, 'status': 'completed'}, # Reggae
        {'user_idx': 7, 'event_idx': 10, 'quantity': 1, 'status': 'completed'}, # Metal
    ]

    orders = []
    for order_data in orders_data:
        if order_data['user_idx'] < len(users) and order_data['event_idx'] < len(events):
            order = Order(
                user_id=users[order_data['user_idx']].id,
                status=order_data['status']
            )
            db.session.add(order)
            db.session.flush()  # Ensure order ID is available

            ticket = Ticket(
                order_id=order.id,
                event_id=events[order_data['event_idx']].id,
                quantity=order_data['quantity']
            )
            db.session.add(ticket)
            orders.append(order)

    db.session.commit()
    return orders

def create_sample_comments(users, events):
    """Create sample comments for various events"""
    comments_data = [
        # Comments for Rock Festival
        {'user_idx': 1, 'event_idx': 0, 'body': 'So excited for this rock festival! The lineup looks absolutely incredible. Can\'t wait to see the headliners!'},
        {'user_idx': 4, 'event_idx': 0, 'body': 'Been waiting all year for this. Rock festivals at Riverstage are always amazing!'},
        {'user_idx': 8, 'event_idx': 0, 'body': 'Anyone know what time the gates open? Want to get there early for the best spot!'},
        
        # Comments for Electronic
        {'user_idx': 2, 'event_idx': 1, 'body': 'Electronic music showcase at The Tivoli is going to be mind-blowing! The sound system there is perfect for this genre.'},
        {'user_idx': 5, 'event_idx': 1, 'body': 'Love the electronic scene in Brisbane. This lineup is stacked with talent!'},
        
        # Comments for Pop Concert
        {'user_idx': 3, 'event_idx': 2, 'body': 'Pop stars live is going to be incredible! Already got my tickets and I\'m counting down the days.'},
        {'user_idx': 7, 'event_idx': 2, 'body': 'The Brisbane Entertainment Centre is perfect for this kind of show. Great acoustics!'},
        
        # Comments for Jazz Evening
        {'user_idx': 4, 'event_idx': 3, 'body': 'Love intimate jazz performances. Brisbane Jazz Club has such a cozy atmosphere.'},
        {'user_idx': 9, 'event_idx': 3, 'body': 'Jazz music in a small venue hits different. Can\'t wait for this evening!'},
        
        # Comments for Hip Hop
        {'user_idx': 5, 'event_idx': 4, 'body': 'Underground hip hop is where the real talent is. This is going to be fire!'},
        {'user_idx': 11, 'event_idx': 4, 'body': 'The Foundry is the perfect venue for underground hip hop. Raw and authentic!'},
        
        # Comments for Classical
        {'user_idx': 6, 'event_idx': 5, 'body': 'Queensland Symphony Orchestra never disappoints. Classical music at QPAC is pure magic.'},
        {'user_idx': 1, 'event_idx': 5, 'body': 'Love a good symphony gala. The acoustics at the Concert Hall are phenomenal!'},
        
        # Comments for Free Folk
        {'user_idx': 7, 'event_idx': 6, 'body': 'Love that this folk festival is free! Community events like this are so important.'},
        {'user_idx': 10, 'event_idx': 6, 'body': 'New Farm Park is the perfect setting for a folk festival. Family-friendly and beautiful location!'},
        
        # Comments for Blues & BBQ
        {'user_idx': 8, 'event_idx': 7, 'body': 'Blues and BBQ - perfect combination for a weekend festival! Roma Street Parkland is a great venue.'},
        {'user_idx': 3, 'event_idx': 7, 'body': 'Can\'t wait to try the BBQ while listening to some authentic blues music!'},
        
        # Comments for Country
        {'user_idx': 9, 'event_idx': 8, 'body': 'Country music jamboree sounds like a great time! Love the line dancing component.'},
        {'user_idx': 2, 'event_idx': 8, 'body': 'RNA Showgrounds is perfect for country music events. Lots of space and good vibes!'},
        
        # Comments for Reggae
        {'user_idx': 10, 'event_idx': 9, 'body': 'Reggae at sunset sounds absolutely perfect. Howard Smith Wharves has the best river views!'},
        {'user_idx': 6, 'event_idx': 9, 'body': 'Chill reggae vibes by the Brisbane River - this is going to be so relaxing!'},
        
        # Comments for Metal
        {'user_idx': 11, 'event_idx': 10, 'body': 'Metal mayhem at The Triffid! This venue has the best sound for heavy music.'},
        {'user_idx': 4, 'event_idx': 10, 'body': 'Ready for some thunderous drums and brutal riffs! This is going to be intense!'},
        
        # Comments for Indie
        {'user_idx': 1, 'event_idx': 11, 'body': 'Love discovering new indie acts. The Zoo is perfect for finding the next big thing!'},
        {'user_idx': 8, 'event_idx': 11, 'body': 'Indie music discovery events are so cool. You never know what amazing talent you\'ll find!'},
        
        # Comments for past events
        {'user_idx': 5, 'event_idx': 15, 'body': 'That jazz night at Blue Moon was absolutely incredible! The musicians were so talented.'},
        {'user_idx': 6, 'event_idx': 16, 'body': 'Last year\'s rock concert was one of the best I\'ve ever been to. Hope they do it again!'},
        
        # Comments for sold out event
        {'user_idx': 8, 'event_idx': 18, 'body': 'So lucky to get tickets to this exclusive acoustic session! It\'s going to be so intimate.'},
        {'user_idx': 9, 'event_idx': 18, 'body': 'Acoustic sessions in small venues are the best. You can really connect with the music.'},
        
        # Additional random comments
        {'user_idx': 2, 'event_idx': 12, 'body': 'R&B and soul music always gets me in the mood. Princess Theatre is a classy venue!'},
        {'user_idx': 3, 'event_idx': 13, 'body': 'Punk rock rebellion sounds intense! Ready for some fast and loud music.'},
        {'user_idx': 4, 'event_idx': 14, 'body': 'Alternative rock bands are always pushing boundaries. Excited to hear some unique sounds!'},
        {'user_idx': 7, 'event_idx': 17, 'body': 'Virtual reality music experience? This sounds like the future of concerts!'},
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