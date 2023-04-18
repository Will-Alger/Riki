"""
    Forms
    ~~~~~
"""
from flask_wtf import Form
from wtforms import BooleanField
from wtforms import TextField
from wtforms import TextAreaField
from wtforms import PasswordField
from wtforms import StringField, validators
from wtforms.validators import InputRequired
from wtforms.validators import ValidationError

from wiki.core import clean_url
from wiki.web import current_wiki
from wiki.web import current_users
from flask import flash
from wiki.web.userDAO import UserDao
from werkzeug.security import generate_password_hash, check_password_hash


class URLForm(Form):
    url = TextField('', [InputRequired()])

    def validate_url(form, field):
        if current_wiki.exists(field.data):
            raise ValidationError('The URL "%s" exists already.' % field.data)

    def clean_url(self, url):
        return clean_url(url)


class SearchForm(Form):
    term = TextField('', [InputRequired()])
    ignore_case = BooleanField(
        description='Ignore Case',
        # FIXME: default is not correctly populated
        default=True)


class EditorForm(Form):
    title = TextField('', [InputRequired()])
    body = TextAreaField('', [InputRequired()])
    tags = TextField('')


class LoginForm(Form):
    email = StringField(label='E-mail', validators=[
        validators.Length(min=5, max=35),
        validators.Email()
    ])
    password = PasswordField('', [InputRequired()])

    def validate_email(form, field):
        user = current_users.get_user(field.data)
        if user is None:
            raise ValidationError('This username does not exist.')

    def validate_password(form, field):
        user = current_users.get_user(form.email.data)
        if user is not None:
            password_authenticated = user.check_password(field.data)

            if not password_authenticated:
                raise ValidationError('Username and password do not match.')


class SignupForm(Form):
    first_name = TextField('', [InputRequired()])
    last_name = TextField('', [InputRequired()])

    email = StringField(label='E-mail', validators=[
        validators.Length(min=5, max=35),
        validators.Email()
    ])
    password = PasswordField('', validators=[
        validators.Length(min=2, message='Too short'),
        InputRequired(),
    ])
    confirm_password = PasswordField('', validators=[
        InputRequired(),
        validators.EqualTo('password', message='Passwords must match'),
    ])

    def validate_email(form, field):
        valemail =  current_users.get_user(field.data)
        flash(f'val email -> {valemail}')
        if valemail is not None:
            raise ValidationError('This Email ID is already registered. Please login')
