from flask_wtf import FlaskForm
from wtforms.fields import EmailField, StringField, PasswordField, SubmitField,StringField, TextAreaField, DateField, IntegerField, FileField
from wtforms.validators import InputRequired, EqualTo,DataRequired
from flask_wtf.file import FileField, FileAllowed
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

class editForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    time = StringField('Time', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    capacity = IntegerField('Capacity')
    image = FileField('Event Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])

class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    date = DateField('Date', validators=[DataRequired()])
    time = StringField('Time', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    capacity = IntegerField('Capacity')
    image = FileField('Image')