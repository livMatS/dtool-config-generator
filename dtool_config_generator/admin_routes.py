# https://uniwebsidad.com/libros/explore-flask/chapter-12/email-confirmation
import logging

from flask_smorest import Blueprint

bp = Blueprint("admin", __name__, template_folder='templates', url_prefix='/admin')


logger = logging.getLogger(__name__)
