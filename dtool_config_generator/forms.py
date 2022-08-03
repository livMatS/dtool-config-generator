from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class ConfirmationForm(FlaskForm):
    pass


class ProfileForm(FlaskForm):
    name = StringField('Full name', validators=[DataRequired()])
    email = StringField('Email address', validators=[DataRequired()])
    orcid = StringField('ORCID')
