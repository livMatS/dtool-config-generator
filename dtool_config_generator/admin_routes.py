from flask_admin.contrib.sqla import ModelView
from flask_smorest import Blueprint
from dtool_config_generator import admin, db

from .models import User

bp = Blueprint('admin', __file__, url_prefix='/admin')
admin.add_view(ModelView(User, db.session))
