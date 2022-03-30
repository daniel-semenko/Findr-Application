from app.Model.models import User, Language, Field, Class

from flask_wtf import FlaskForm
from flask_login import current_user

from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.fields.core import BooleanField, IntegerField
from wtforms.fields.simple import PasswordField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Email, Length
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput

def get_languages():
    return Language.query.all()

def get_fields():
    return Field.query.all()

def get_electives():
    return Class.query.all()

class StudentRegistrationForm(FlaskForm):
    firstname = StringField('First Name',validators=[DataRequired()])
    lastname = StringField('Last Name',validators=[DataRequired()])
    wsuid = StringField('WSU ID', validators=[DataRequired()])
    phone = IntegerField('Phone Number', validators=[DataRequired()])
    username = StringField('Username (WSU Email)', validators=[DataRequired(), Email()])
    email = StringField('Contact Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_wsuid(self, wsuid):
        user = User.query.filter_by(wsuid=wsuid.data).first()
        if user is not None:
            raise ValidationError('This WSU ID already exists! Please use a different WSU ID.')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This email already exists! Please use a different email address.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email already exists! Please use a different email address.')

    def validate_phone(self, phone):
        user = User.query.filter_by(phone=phone.data).first()
        if user is not None:
            raise ValidationError('This phone number already exists! Please use a different phone number.')

class FacultyRegistrationForm(FlaskForm):
    firstname = StringField('First Name',validators=[DataRequired()])
    lastname = StringField('Last Name',validators=[DataRequired()])
    wsuid = StringField('WSU ID', validators=[DataRequired()])
    phone = IntegerField('Phone Number', validators=[DataRequired()])
    username = StringField('Username (WSU Email)', validators=[DataRequired(), Email()])
    email = StringField('Contact Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_wsuid(self, wsuid):
        user = User.query.filter_by(wsuid=wsuid.data).first()
        if user is not None:
            raise ValidationError('This WSU ID already exists! Please use a different WSU ID.')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This email already exists! Please use a different email address.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email already exists! Please use a different email address.')

    def validate_phone(self, phone):
        user = User.query.filter_by(phone=phone.data).first()
        if user is not None:
            raise ValidationError('This phone number already exists! Please use a different phone number.')

class LoginForm(FlaskForm):
    username = StringField('Username (WSU Email)',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class EditForm(FlaskForm):
    username = StringField('Username (Your WSU Email)',validators=[DataRequired(), Email()])
    firstname = StringField('First Name',validators=[DataRequired()])
    lastname = StringField('Last Name',validators=[DataRequired()])
    wsuid = StringField('WSU ID', validators=[DataRequired()])
    major = StringField('Major', validators=[DataRequired()])
    gpa = StringField('Cumulative GPA', validators=[DataRequired()])
    graddate = StringField('Expected Graduation Date', validators=[DataRequired()])
    phone = IntegerField('Phone Number', validators=[DataRequired()])
    email = StringField('Contact Email',validators=[DataRequired(), Email()])
    prior_experience = TextAreaField('Prior Experience', validators=[DataRequired(), Length(min=1, max=1500)])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    languages = QuerySelectMultipleField('Languages',
                                         query_factory=get_languages,
                                         get_label=lambda x: x.name,
                                         widget=ListWidget(prefix_label=False),
                                         option_widget=CheckboxInput())
    fields = QuerySelectMultipleField('Fields',
                                      query_factory=get_fields,
                                      get_label=lambda x: x.name,
                                      widget=ListWidget(prefix_label=False),
                                      option_widget=CheckboxInput())
    electives = QuerySelectMultipleField('Electives',
                                         query_factory=get_electives,
                                         get_label=lambda x:
                                         x.coursenum + ' - ' + x.title,
                                         widget=ListWidget(prefix_label=False),
                                         option_widget=CheckboxInput())
    submit = SubmitField('Submit')

    def validate_wsuid(self, wsuid):
        users = User.query.filter_by(wsuid = wsuid.data).all()
        for user in users:
            if (user.id != current_user.id):
                raise ValidationError('This WSU ID is already being used! Please use a different WSU ID!')

    def validate_username(self, username):
        users = User.query.filter_by(username = username.data).all()
        for user in users:
            if (user.id != current_user.id):
                raise ValidationError('This email is already being used! Please use a different email!')

    def validate_email(self, email):
        users = User.query.filter_by(email = email.data).all()
        for user in users:
            if (user.id != current_user.id):
                raise ValidationError('This email is already being used! Please use a different email!')

    def validate_phone(self, phone):
        users = User.query.filter_by(phone = phone.data).all()
        for user in users:
            if (user.id != current_user.id):
                raise ValidationError('This phone number is already being used! Please use a different phone number!')
