import pickle
from functools import wraps

from app.modules.elevator import REDIS_PREFIX, bp
from app.modules.redis import get_redis
from flask import g, request


def authorized(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'elctx' not in g:
            return 'Authorization required', 401
        return func(*args, **kwargs)
    return decorated_function


@bp.before_request
def load_elctx():
    token = request.headers.get('X-Auth-Token')

    if not token:
        return

    g.token = token
    g.elctx = get_elctx(token)


def get_elctx(token):
    redis = get_redis()
    key = REDIS_PREFIX + token
    elctx = None

    if redis.exists(key):
        elctx = pickle.loads(redis.get(key))

    return elctx


def store_elctx(token, elctx):
    if not token:
        raise Exception('token is not valid')

    redis = get_redis()
    key = REDIS_PREFIX + token

    redis.set(key, pickle.dumps(elctx))

    if elctx.is_end:
        redis.rpush(REDIS_PREFIX + 'finish', token)


def get_all_tokens():
    redis = get_redis()
    key = REDIS_PREFIX + 'tokens'
    return redis.lrange(key, 0, -1)


def get_finished_tokens():
    redis = get_redis()
    key = REDIS_PREFIX + 'finish'

    if not redis.exists(key):
        return []

    return redis.lrange(key, 0, -1)
