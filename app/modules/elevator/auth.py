from functools import wraps
from flask import request
from flask import g
import pickle

from app.modules.elevator import bp
from app.modules.redis import get_redis

def authorized(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'elctx' not in g:
            return 'Authorization required', 401
        return func(*args, **kwargs)
    return decorated_function

@bp.before_request
def load_elctx():
    redis = get_redis()
    token = request.headers.get('X-Auth-Token')

    if not token:
        return
    
    g.token = token
    key = 'elevator:' + token
    if redis.exists(key):
        g.elctx = pickle.loads(redis.get(key))

def store_elctx(token, elctx):
    if not token:
        raise Exception('token is not valid')
    
    redis = get_redis()
    key = 'elevator:' + token

    redis.set(key, pickle.dumps(elctx))
