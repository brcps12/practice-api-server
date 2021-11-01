import pickle
from functools import wraps

from app.modules.redis import get_redis
from app.modules.tbike import REDIS_PREFIX, bp
from flask import g, request


def authorized(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if 'tbike' not in g:
            return 'Authorization required', 401
        return func(*args, **kwargs)
    return decorated_function


@bp.before_request
def load_tbike():
    token = request.headers.get('Authorization')

    if not token:
        return

    g.token = token
    g.tbike = get_tbike(token)


def get_tbike(token):
    redis = get_redis()
    key = REDIS_PREFIX + token
    tbike = None

    if redis.exists(key):
        tbike = pickle.loads(redis.get(key))

    return tbike


def store_tbike(token, tbike):
    if not token:
        raise Exception('token is not valid')

    redis = get_redis()
    key = REDIS_PREFIX + token

    redis.set(key, pickle.dumps(tbike))

    if tbike.status == 'finished':
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
