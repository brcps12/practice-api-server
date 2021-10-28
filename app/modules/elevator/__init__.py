# flake8: noqa
from flask import Blueprint


bp = Blueprint('elevator', __name__, url_prefix='/elevator',
               static_url_path='/static', static_folder='./static',
               template_folder='./template')

REDIS_PREFIX = 'elevator:'


import app.modules.elevator.routes
import app.modules.elevator.dataset
import app.modules.elevator.cli
