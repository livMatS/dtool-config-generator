# Inspired by
# https://stackoverflow.com/questions/42909816/can-i-avoid-circular-imports-in-flask-and-sqlalchemy
# https://github.com/jamescurtin/demo-cookiecutter-flask/blob/master/my_flask_app/extensions.py
from flask_admin import Admin
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
ma = Marshmallow()
admin = Admin(name='dtool-config-generator', template_mode='bootstrap3')
