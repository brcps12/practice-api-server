from app.modules.elevator import REDIS_PREFIX, bp
from app.modules.elevator import dataset
from app.modules.redis import get_redis


@bp.cli.command()
def generate():
    dataset.appeach_mansion()
    dataset.jayg_building()
    dataset.ryan_tower()

@bp.cli.command()
def clean_redis():
    redis = get_redis()
    key = REDIS_PREFIX + 'tokens'
    tokens = [token.decode('ascii') for token in redis.lrange(key, 0, -1)]

    for token in tokens:
        redis.delete(REDIS_PREFIX + token)

    redis.delete(key)
    redis.delete(REDIS_PREFIX + 'finish')
