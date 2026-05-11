from flask import Blueprint

bp = Blueprint('receitas_mensais', __name__)

from . import routes  # noqa
