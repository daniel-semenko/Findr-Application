from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.fields.core import BooleanField
from wtforms.validators import  DataRequired, Length
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput

from app.Model.models import Post, Field

def get_field():
    return Field.query.all()

def get_fieldname(theField):
    return theField.name

class PostForm(FlaskForm):
    title = StringField('Project Title', validators=[DataRequired()])
    goals = TextAreaField('Research Goals', validators=[DataRequired(), Length(min=1, max=300)])
    qualifications = TextAreaField('Qualifications', validators=[DataRequired(), Length(min=1, max=300)])
    startdate = StringField('Start Date', validators=[DataRequired(), Length(min=1, max=20)])
    enddate = StringField('End Date', validators=[DataRequired(), Length(min=1, max=20)])
    commitment = TextAreaField('Commitments', validators=[DataRequired(), Length(min=1, max=300)])
    fields = QuerySelectMultipleField('Fields', query_factory= get_field, get_label= get_fieldname, widget=ListWidget(prefix_label=False), option_widget=CheckboxInput() )
    submit = SubmitField('Post')

class SortForm(FlaskForm):
    sort = SelectField('Sort', choices=['Title', 'Start Date', 'Post Date'])
    sortbyrecommendedposts = BooleanField('Display recommended research posts only.')
    submit = SubmitField('Refresh')
