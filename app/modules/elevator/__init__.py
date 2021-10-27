from flask import Blueprint

bp = Blueprint('elevator', __name__, url_prefix='/elevator')

import app.modules.elevator.routes
