from flask_wtf import FlaskForm
from wtforms.fields import (
    EmailField, StringField, PasswordField, SubmitField, 
    TextAreaField, DateField, IntegerField, FileField, TimeField, DecimalField, HiddenField
)
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, NumberRange, EqualTo, DataRequired, Optional, Length, Regexp

from riffhub.models import Genre

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
        InputRequired(),
        Length(min=3, max=80, message="Username must be between 3 and 80 characters")
    ])
    email = EmailField("Email", validators=[InputRequired()])
    first_name = StringField("First Name", validators=[
        InputRequired(),
        Length(min=1, max=50, message="First name must be between 1 and 50 characters")
    ])
    surname = StringField("Surname", validators=[
        InputRequired(),
        Length(min=1, max=50, message="Surname must be between 1 and 50 characters")
    ])
    contact_number = StringField("Contact Number", validators=[
        InputRequired(),
        Length(min=10, max=20, message="Contact number must be between 10 and 20 characters"),
        Regexp(r'^[\d\s\-\+\(\)]+$', message="Contact number can only contain digits, spaces, hyphens, plus signs, and parentheses")
    ])
    street_address = TextAreaField("Street Address", validators=[
        InputRequired(),
        Length(min=5, max=200, message="Street address must be between 5 and 200 characters")
    ])
    password = PasswordField("Password", validators=[
        InputRequired(),
        Length(min=6, message="Password must be at least 6 characters long")
    ])
    confirm = PasswordField("Confirm Password", validators=[
        InputRequired(), 
        EqualTo('password', "Please ensure your passwords are the same")
    ])
    submit = SubmitField("Register")

class CommentForm(FlaskForm):
    body = StringField("Comment", validators=[InputRequired()])
    submit = SubmitField("Post Comment")

class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    genre = QuerySelectField(
        'Genre',
        query_factory=lambda: Genre.query.order_by(Genre.title).all(),
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


class GenreForm(FlaskForm):
    name = StringField('Genre Name', validators=[DataRequired()])
    submit = SubmitField('Add Genre')


class OrderTicketsForm(FlaskForm):
    quantity = IntegerField('Number of Tickets', validators=[InputRequired()])
    submit = SubmitField('Place Order')


    def __init__(self, max_tickets=100, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quantity.validators.append(NumberRange(min=1, max=max_tickets, message=f"You can only order up to {max_tickets} tickets."))
        
class CancelTicketsForm(FlaskForm):
    event_id = HiddenField('Event ID')
    submit = SubmitField('Cancel')
    
class ProfileEditForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(),
        Length(min=3, max=80, message="Username must be between 3 and 80 characters")
    ])
    email = EmailField("Email", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[
        DataRequired(),
        Length(min=1, max=50, message="First name must be between 1 and 50 characters")
    ])
    surname = StringField("Surname", validators=[
        DataRequired(),
        Length(min=1, max=50, message="Surname must be between 1 and 50 characters")
    ])
    contact_number = StringField("Contact Number", validators=[
        DataRequired(),
        Length(min=10, max=20, message="Contact number must be between 10 and 20 characters"),
        Regexp(r'^[\d\s\-\+\(\)]+$', message="Contact number can only contain digits, spaces, hyphens, plus signs, and parentheses")
    ])
    street_address = TextAreaField("Street Address", validators=[
        DataRequired(),
        Length(min=5, max=200, message="Street address must be between 5 and 200 characters")
    ])
    submit = SubmitField("Update Profile")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long")
    ])
    confirm_password = PasswordField("Confirm New Password", 
                                   validators=[DataRequired(), 
                                             EqualTo('new_password', 
                                                   message='Passwords must match')])
    submit = SubmitField("Change Password")


class DeleteEventForm(FlaskForm):
    submit = SubmitField('Delete Event')