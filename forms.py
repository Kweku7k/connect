from flask_wtf import FlaskForm
from wtforms import EmailField, StringField, PasswordField, DateField, FloatField,SubmitField, BooleanField, SelectField, IntegerField, RadioField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from wtforms.widgets import TextArea

class BroadcastForm(FlaskForm):
    group = SelectField('Group', choices=[('All Contacts - 30 contacts')])
    senderId = SelectField('SenderId', choices=[('PrsConnect')])
    message = StringField('Message',widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField('Broadcast')

class AddUserForm(FlaskForm):
    group = SelectField('Group', choices=[('All Contacts - 30 contacts')])
    name = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    email = StringField('Email')
    picture = StringField('Image')
    submit = SubmitField('Add Contact')


