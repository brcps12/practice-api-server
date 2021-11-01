# flake8: noqa
from flask import Blueprint

bp = Blueprint('tbike', __name__, url_prefix='/tbike')

REDIS_PREFIX = 'tbike:'


import app.modules.tbike.auth
import app.modules.tbike.routes
