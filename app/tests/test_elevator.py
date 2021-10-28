import pytest
from app import create_app
from redislite import Redis

URL_PREFIX = '/elevator'
USER_KEY = 'testuserkey'


@pytest.fixture
def client(mocker):
    redis_mock = Redis('/tmp/redis.db')
    mocker.patch('app.modules.redis.get_redis', return_value=redis_mock)
    app = create_app()

    with app.test_client() as client:
        yield client

    redis_mock.close()


def test_start(client):
    res = client.post(URL_PREFIX + '/start/' + USER_KEY + '/0/1')
    assert res.status_code == 200, 'status code should be 200'

    res = client.post(URL_PREFIX + '/start/' + USER_KEY + '/10/10')
    assert res.status_code != 200, 'request should not be success'


def test_action(client,):
    # Number of elevators is 4
    res = client.post(URL_PREFIX + '/start/' + USER_KEY + '/0/4')
    data = res.get_json()

    token = data.get('token')
    elevators = data.get('elevators')

    headers = {
        'X-Auth-Token': token
    }

    commands = [{'elevator_id': el.get('id'), 'command': 'OPEN'} for el in elevators]

    res = client.post(URL_PREFIX + '/action', headers=headers, json={
        'commands': commands
    })

    assert res.status_code == 200, 'valid action, should be success'

    res = client.post(URL_PREFIX + '/action', headers=headers, json={
        'commands': commands[0:2]
    })

    assert res.status_code != 200, 'lack of commands'

    commands[-1]['elevator_id'] = 0
    res = client.post(URL_PREFIX + '/action', headers=headers, json={
        'commands': commands
    })

    assert res.status_code != 200, 'commands contains duplicated elevator'

    commands[-1]['elevator_id'] = 4
    res = client.post(URL_PREFIX + '/action', headers=headers, json={
        'commands': commands
    })

    assert res.status_code != 200, 'elevator id is over valid range'
