from flask import Blueprint

bp = Blueprint('trader', __name__)

from . import routes  # noqa
