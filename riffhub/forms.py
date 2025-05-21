from flask_wtf import FlaskForm
from wtforms.fields import EmailField, StringField, PasswordField, SubmitField, TextAreaField, DateField, IntegerField, FileField, TimeField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import InputRequired, EqualTo, DataRequired
from flask_wtf.file import FileField
from riffhub.models import Genre

class loginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class registerForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo('password', "Please ensure your passwords are the same")])
    submit = SubmitField("Register")

class commentForm(FlaskForm):
    body = StringField("Comment", validators=[InputRequired()])
    submit = SubmitField("Post Comment")

class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
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
    capacity = IntegerField('Capacity')
    image = FileField('Image')
    submit = SubmitField('Save Event')

class GenreForm(FlaskForm):
    name = StringField('Genre Name', validators=[DataRequired()])
    submit = SubmitField('Add Genre')
