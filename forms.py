from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, FloatField,SubmitField, BooleanField, SelectField, IntegerField, RadioField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from wtforms.widgets import TextArea

class BroadcastForm(FlaskForm):
    group = SelectField('Group', choices=[('All Contacts - 30 contacts')])
    senderId = SelectField('SenderId', choices=[('PrsConnect')])
    message = StringField('Message',widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField('Broadcast')

class BroadcastEmailForm(FlaskForm):
    group = SelectField('Group', choices=[('All Contacts - 30 contacts')])
    title = StringField('Title', validators=[DataRequired()])
    subject = StringField('Subject',validators=[DataRequired()])
    message = StringField('Message',widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField('Broadcast')

class AddUserForm(FlaskForm):
    group = SelectField('Group', choices=[('All Contacts - 30 contacts')])
    name = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    email = StringField('Email')
    picture = StringField('Image')
    submit = SubmitField('Add Contact')


class TakePayment(FlaskForm):
    # name = StringField('Name', validators=[DataRequired()])
    reference = StringField('Name')
    # number = StringField('Number', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=10, message="This field needs to be exactly 10 figures")])
    network = SelectField('Network', choices=[('MTN', 'MTN'), ('AIRTELTIGO','AIRTELTIGO'),('VODAFONE', 'VODAFONE')])
    amount = FloatField('Amount', validators=[DataRequired()])
    note = StringField('Note')
    # market = SelectField('How did you hear about central university before coming here.', choices=[('Media/Newspaper', 'Media/Newspaper'),('Friend or Relative', 'Friend or Relative'),('The Internet', 'The Internet'),('Outreach Programme', 'Outreach Programme')])
    # recommendation = BooleanField('Would you recommend Central University to a potential applicant')
    submit = SubmitField('Pay')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RegisterForm(FlaskForm):
    username = StringField('Name', validators=[DataRequired()])
    appId = StringField('appId', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=13, message="Your phone number should be more than 10 digits and less than 15")])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('password', message='Your passwords dont match, please try again')])
    submit = SubmitField('Update')