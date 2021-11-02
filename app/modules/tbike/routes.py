
import random

from app.modules.redis import get_redis
from app.modules.tbike import REDIS_PREFIX, bp
from app.modules.tbike.auth import authorized, store_tbike
from app.modules.tbike.eval import eval_tbike
from app.modules.tbike.tbike_system import TBikeSystem
from flask import g, request

letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def generate_auth_key():
    return ''.join(random.sample(letters, 5))


@bp.route('/start', methods=['POST'])
def start():
    data = request.get_json()
    problem = int(data.get('problem'))

    if not 1 <= problem <= 2:
        return 'Problem should match to 1 or 2', 400

    auth_key = generate_auth_key()

    tbike = TBikeSystem(problem)
    store_tbike(auth_key, tbike)

    redis = get_redis()
    redis.rpush(REDIS_PREFIX + 'tokens', auth_key)

    return {
        'auth_key': auth_key,
        'problem': problem,
        'time': tbike.time
    }


@bp.route('/locations', methods=['GET'])
@authorized
def get_locations():
    return {'locations': [loc.to_json() for loc in g.tbike.locations]}


@bp.route('/trucks', methods=['GET'])
@authorized
def get_trucks():
    return {'trucks': [truck.to_json() for truck in g.tbike.trucks]}


@bp.route('/simulate', methods=['PUT'])
@authorized
def simulate():
    data = request.get_json()
    commands = data.get('commands', [])

    response = g.tbike.simulate(commands)
    store_tbike(g.token, g.tbike)

    return response


@bp.route('/score', methods=['GET'])
@authorized
def score():
    return {'score': eval_tbike(g.tbike)}
