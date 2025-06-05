from flask_wtf import FlaskForm
from wtforms.fields import (
    EmailField, StringField, PasswordField, SubmitField, 
    TextAreaField, DateField, IntegerField, FileField, TimeField, DecimalField, HiddenField
)
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, NumberRange, EqualTo, DataRequired, Optional

from riffhub.models import Genre


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo('password', "Please ensure your passwords are the same")])
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