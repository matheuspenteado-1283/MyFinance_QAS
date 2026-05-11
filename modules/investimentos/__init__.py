from flask import Blueprint

bp = Blueprint('investimentos', __name__)

from . import routes  # noqa
