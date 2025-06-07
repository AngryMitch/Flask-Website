# Import necessary form fields and validators from WTForms and Flask-WTF
from flask_wtf import FlaskForm
from wtforms.fields import (
    EmailField, StringField, PasswordField, SubmitField, 
    TextAreaField, DateField, IntegerField, FileField, TimeField, DecimalField, HiddenField
)
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, NumberRange, EqualTo, DataRequired, Optional, Length, Regexp

# Import Genre model for dynamic genre selection
from riffhub.models import Genre

# Form for user login
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])  # Required username field
    password = PasswordField("Password", validators=[InputRequired()])  # Required password field
    submit = SubmitField("Login")  # Submit button

# Form for new user registration
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
        InputRequired(),
        Length(min=3, max=80, message="Username must be between 3 and 80 characters")
    ])
    email = EmailField("Email", validators=[InputRequired()])
    first_name = StringField("First Name", validators=[
        InputRequired(),
        Length(min=1, max=50)
    ])
    surname = StringField("Surname", validators=[
        InputRequired(),
        Length(min=1, max=50)
    ])
    contact_number = StringField("Contact Number", validators=[
        InputRequired(),
        Length(min=10, max=20),
        Regexp(r'^[\d\s\-\+\(\)]+$', message="Only digits and phone symbols allowed")
    ])
    street_address = TextAreaField("Street Address", validators=[
        InputRequired(),
        Length(min=5, max=200)
    ])
    password = PasswordField("Password", validators=[
        InputRequired(),
        Length(min=6)
    ])
    confirm = PasswordField("Confirm Password", validators=[
        InputRequired(), 
        EqualTo('password', message="Please ensure your passwords are the same")
    ])
    submit = SubmitField("Register")

# Form for submitting a comment
class CommentForm(FlaskForm):
    body = StringField("Comment", validators=[InputRequired()])  # Comment body
    submit = SubmitField("Post Comment")  # Submit button

# Form for creating or editing an event
class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    genre = QuerySelectField(
        'Genre',
        query_factory=lambda: Genre.query.order_by(Genre.title).all(),  # Fetch genres from DB
        get_label='title',
        allow_blank=True,
        blank_text='— Select a Genre —',
        validators=[DataRequired()]
    )
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', format="%H:%M", validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[Optional()])
    price = DecimalField('Price', validators=[DataRequired()])
    image = FileField('Image', validators=[Optional()])
    submit = SubmitField('Save Event')

# Form for adding a new genre
class GenreForm(FlaskForm):
    name = StringField('Genre Name', validators=[DataRequired()])  # Required genre name
    submit = SubmitField('Add Genre')

# Form for ordering tickets to an event
class OrderTicketsForm(FlaskForm):
    quantity = IntegerField('Number of Tickets', validators=[InputRequired()])
    submit = SubmitField('Place Order')

    def __init__(self, max_tickets=100, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically add a maximum ticket limit validator
        self.quantity.validators.append(
            NumberRange(min=1, max=max_tickets, message=f"You can only order up to {max_tickets} tickets.")
        )

# Form for cancelling ticket orders
class CancelTicketsForm(FlaskForm):
    event_id = HiddenField('Event ID')  # Hidden field to identify the event
    submit = SubmitField('Cancel')

# Form for editing user profile details
class ProfileEditForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(),
        Length(min=3, max=80)
    ])
    email = EmailField("Email", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[
        DataRequired(),
        Length(min=1, max=50)
    ])
    surname = StringField("Surname", validators=[
        DataRequired(),
        Length(min=1, max=50)
    ])
    contact_number = StringField("Contact Number", validators=[
        DataRequired(),
        Length(min=10, max=20),
        Regexp(r'^[\d\s\-\+\(\)]+$', message="Only digits and phone symbols allowed")
    ])
    street_address = TextAreaField("Street Address", validators=[
        DataRequired(),
        Length(min=5, max=200)
    ])
    submit = SubmitField("Update Profile")

# Form for changing user password
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField("Confirm New Password", validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField("Change Password")

# Form to confirm event deletion
class DeleteEventForm(FlaskForm):
    submit = SubmitField('Delete Event')
