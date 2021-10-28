from functools import wraps
from shutil import Error
from flask import g
from flask import request
from flask import render_template
from app.modules.elevator.context import ElevatorContext
from app.modules.elevator.erros import CommandError
import random
import json

from app.modules.redis import get_redis
from app.modules.elevator import REDIS_PREFIX, bp
from app.modules.elevator.auth import authorized, get_all_tokens, get_elctx, get_finished_tokens, store_elctx


letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def generate_token():
    return ''.join(random.sample(letters, 5))

@bp.route('/start/<user_key>/<int:problem_id>/<int:number_of_elevators>', methods=['POST', 'GET'])
def start(user_key, problem_id, number_of_elevators):
    if not 0 <= problem_id <= 2:
        return 'Problem ID should be between 0 and 2', 400

    if not 1 <= number_of_elevators <= 4:
        return 'Number of elevators should be between 1 and 4', 400
    
    token = generate_token()
    elctx = ElevatorContext(problem_id, number_of_elevators)
    store_elctx(token, elctx)

    # push token
    key = REDIS_PREFIX + 'tokens'
    redis = get_redis()
    redis.rpush(key, token)

    return {
        'token': token,
        'timestamp': elctx.timestamp,
        'elevators': [el.to_json() for el in elctx.elevators],
        'is_end': elctx.is_end
    }

@bp.route('/oncalls', methods=['GET'])
@authorized
def oncalls():
    return {
        'token': g.token,
        'timestamp': g.elctx.timestamp,
        'elevators': [el.to_json() for el in g.elctx.elevators],
        'calls': [call.to_json() for call in g.elctx.calls],
        'is_end': g.elctx.is_end
    }

@bp.route('/action', methods=['POST'])
@authorized
def action():
    params = request.get_json()
    commands = params.get('commands', [])
    ctx = g.elctx

    if len(commands) != ctx.number_of_elevators:
        return 'Number of commands should match number of elevators', 400

    try:
        commands = sorted(commands, key=lambda x: x.get('elevator_id'))

        for i in range(ctx.number_of_elevators):
            if i != int(commands[i].get('elevator_id')):
                raise Error()
    except Error as e:
        return 'One of elevators\' id is invalid', 400

    if ctx.is_end:
        return {
            'token': g.token,
            'timestamp': ctx.timestamp,
            'elevators': [el.to_json() for el in ctx.elevators],
            'is_end': ctx.is_end
        }

    try:
        for cmd in commands:
            elevator_id = int(cmd.get('elevator_id'))
            command = cmd.get('command')
            call_ids = list(map(int, cmd.get('call_ids', [])))

            if command == 'STOP':
                ctx.stop(elevator_id)
            elif command == 'OPEN':
                ctx.open(elevator_id)
            elif command == 'CLOSE':
                ctx.close(elevator_id)
            elif command == 'ENTER':
                ctx.enter(elevator_id, call_ids)
            elif command == 'EXIT':
                ctx.exit(elevator_id, call_ids)
            elif command == 'UP':
                ctx.up(elevator_id)
            elif command == 'DOWN':
                ctx.down(elevator_id)
            else:
                return 'Wrong command "' + command + '"', 400 
    except CommandError as e:
        return str(e), 400
    except Exception as e:
        return 'Invalid arguments', 400

    ctx.tick()

    store_elctx(g.token, ctx)

    return {
        'token': g.token,
        'timestamp': ctx.timestamp,
        'elevators': [el.to_json() for el in ctx.elevators],
        'is_end': ctx.is_end
    }

@bp.route('/score', methods=['GET'])
@authorized
def score():
    if not g.elctx.is_end:
        return {
            'timestamp': 0
        }
    
    return {
        'timestamp': g.elctx.timestamp
    }

@bp.route('/viewer', methods=['GET'])
def viewer():
    tokens = get_finished_tokens()
    return render_template('viewer-home.html', tokens=[token.decode('ascii') for token in tokens])

@bp.route('/viewer/trials/<token>')
def trial_viewer(token):
    elctx = get_elctx(token)
    if elctx is None or not elctx.is_end:
        return 'Token is invalid', 400
    
    history = elctx.history[:-1]
    return render_template('viewer-trials.html', trials=json.dumps(history))
