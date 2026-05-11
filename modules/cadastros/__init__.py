from flask import Blueprint

bp = Blueprint('cadastros', __name__)

from . import routes  # noqa
