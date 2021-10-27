from flask import current_app
from flask import g
from redis import Redis, ConnectionPool

pool = None

def get_redis():
    if 'redis' not in g:
        g.redis = Redis(connection_pool=pool)
    
    return g.redis

def init_redis():
    global pool
    pool = ConnectionPool(host='redis')