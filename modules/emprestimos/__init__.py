from flask import Blueprint

bp = Blueprint('emprestimos', __name__)

from . import routes  # noqa
