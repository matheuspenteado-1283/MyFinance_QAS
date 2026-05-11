from flask import Blueprint

bp = Blueprint('despesas_mensais', __name__)

from . import routes  # noqa
