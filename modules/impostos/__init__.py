from flask import Blueprint

bp = Blueprint('impostos', __name__)

from . import routes  # noqa
