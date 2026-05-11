from flask import Blueprint

bp = Blueprint('extratos', __name__)

from . import routes  # noqa
