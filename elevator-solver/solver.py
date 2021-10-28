import requests

BASE_URL = 'http://localhost/elevator'
# BASE_URL = 'http://172.26.0.4:8000'
USER_KEY = 'testuser'
PROBLEM_ID = 2
NUMBER_OF_ELEVATORS = 4
ELEVATOR_CAPACITY = 8
MAX_FLOOR = [6, 25, 25][PROBLEM_ID]
WAITING_TIME = [0, 0, 3][PROBLEM_ID]


def list_split(iterable, funcOrList):
    g_false, g_true = [], []
    c_list = funcOrList
    if callable(funcOrList):
        c_list = [funcOrList(item) for item in iterable]

    for item, condition in zip(iterable, c_list):
        (g_false, g_true)[condition].append(item)

    return g_false, g_true


class Command:
    def __init__(self, elevator_id, command, call_ids=None):
        self.elevator_id = elevator_id
        self.command = command
        self.call_ids = call_ids

    def to_json(self):
        result = {
            'elevator_id': self.elevator_id,
            'command': self.command
        }

        if self.command in ['ENTER', 'EXIT']:
            result['call_ids'] = self.call_ids

        return result


class Elevator:
    def __init__(self, id, capacity, max_floor):
        self.id = id
        self.capacity = capacity
        self.max_floor = max_floor
        self.passengers = []
        self.myclients = []

        self.ts = 0
        self.floor = 1
        self.status = 'STOPPED'
        self.upward = True
        self.waiting_time = -1
        self._score = -1
        self._cmd = None

    def clone(self):
        el = Elevator(self.id, self.capacity, self.max_floor)
        el.passengers = [c.clone() for c in self.passengers]
        el.myclients = [c.clone() for c in self.myclients]
        el.ts = self.ts
        el.floor = self.floor
        el.status = self.status
        el.upward = self.upward
        el.waiting_time = self.waiting_time

        return el

    def notify(self):
        self.ts += 1
        if self.waiting_time >= 0:
            self.waiting_time -= 1

    def add_client(self, call):
        self.myclients.append(call)
        self._score = -1
        self._cmd = None

    def remove_client(self, callOrId):
        idx = self.myclients.index(callOrId)
        self.myclients.pop(idx)
        self._score = -1
        self._cmd = None

    def clear_clients(self):
        self.myclients = []
        self._score = -1
        self._cmd = None

    def do_command(self, cmd):
        if cmd.command == 'STOP':
            self.status = 'STOPPED'
        elif cmd.command == 'OPEN':
            self.status = 'OPENED'
        elif cmd.command == 'CLOSE':
            self.status = 'STOPPED'
        elif cmd.command == 'UP':
            self.floor += 1
            self.upward = True
            self.status = 'UPWARD'
        elif cmd.command == 'DOWN':
            self.floor -= 1
            self.upward = False
            self.status = 'DOWNWARD'
        elif cmd.command == 'ENTER':
            self.status = 'OPENED'
            self.myclients, passengers = list_split(self.myclients, lambda p: p.id in cmd.call_ids)
            self.passengers.extend(passengers)
        else:
            self.status = 'OPENED'
            # TODO
            # Don't manage re-enter passengers
            self.passengers = [p for p in self.passengers if p.id not in cmd.call_ids]

            if self.floor == 1:
                self.waiting_time = WAITING_TIME

    def next_command(self):
        _, cmd = self.score()
        if cmd is None:
            if self.status == 'OPENED':
                cmd = Command(self.id, 'OPEN')
            else:
                cmd = Command(self.id, 'STOP')

        self.do_command(cmd)
        return cmd

    def score_if_added(self, call):
        el_cloned = self.clone()
        el_cloned.add_client(call)
        return el_cloned.score()

    def score(self):
        if self._score >= 0:
            return self._score, self._cmd

        score, cmd = self.clone()._score_internal()
        if 0 < self.waiting_time:
            score += self.waiting_time
            cmd = Command(self.id, 'OPEN')
        self._score = score
        self._cmd = cmd
        return score, cmd

    def _score_internal(self):
        score = 0
        cmd = None

        while True:
            if len(self.passengers) + len(self.myclients) == 0:
                break

            curfloor = {
                'enter': [c for c in self.myclients if c.start == self.floor],
                'exit': [c for c in self.passengers if c.end == self.floor]
            }

            if curfloor['exit']:
                # remain_passengers, exit_passengers = list_split(self.passengers, curfloor['exit'])
                _s, _c = self.exit(curfloor['exit'])
                score += _s
                cmd = cmd or _c

            remain_places = self.capacity - len(self.passengers)
            if remain_places > 0 and curfloor['enter']:
                # remain_clients, enter_clients = list_split(self.myclients, curfloor['enter'])
                enter_clients = sorted(curfloor['enter'], key=lambda x: x.end, reverse=self.upward)
                enter_clients = enter_clients[:remain_places]
                _s, _c = self.enter(enter_clients)
                score += _s
                cmd = cmd or _c

            calls = [*self.passengers, *self.myclients]

            if not calls:
                break

            min_floor, max_floor = min(min(c.start, c.end) for c in calls), max(max(c.start, c.end) for c in calls)

            if self.upward:
                if self.floor >= max_floor:
                    self.upward = False
            else:
                if self.floor <= min_floor:
                    self.upward = True

            if self.upward:
                _s, _c = self.up()
                score += _s
                cmd = cmd or _c
            else:
                _s, _c = self.down()
                score += _s
                cmd = cmd or _c

        return score, cmd

    def stop(self):
        if self.status == 'STOPPED':
            return 0, None

        count = 0
        cmd = None

        if self.status in ['UPWARD', 'DOWNWARD']:
            count += 1
            cmd = cmd or Command(self.id, 'STOP')

        if self.status == 'OPENED':
            count += 1
            cmd = cmd or Command(self.id, 'CLOSE')

        self.status = 'STOPPED'
        return count, cmd

    def open(self):
        if self.status == 'OPENED':
            return 0, None

        count, cmd = self.stop()
        cmd = cmd or Command(self.id, 'OPEN')
        self.status = 'OPENED'
        return count + 1, cmd

    def close(self):
        return self.stop()

    def up(self):
        if self.status == 'UPWARD':
            self.floor += 1
            if self.floor > self.max_floor:
                raise Exception()
            return 1, Command(self.id, 'UP')

        count, cmd = self.stop()
        cmd = cmd or Command(self.id, 'UP')
        self.floor += 1
        self.status = 'UPWARD'
        return count + 1, cmd

    def down(self):
        if self.status == 'DOWNWARD':
            self.floor -= 1
            if self.floor < 1:
                raise Exception()
            return 1, Command(self.id, 'DOWN')

        count, cmd = self.stop()
        cmd = cmd or Command(self.id, 'DOWN')
        self.floor -= 1
        self.status = 'DOWNWARD'
        return count + 1, cmd

    def enter(self, passengers):
        count, cmd = self.open()
        self.passengers.extend(passengers)
        if len(self.passengers) > self.capacity:
            raise Exception()
        cmd = cmd or Command(self.id, 'ENTER', [p.id for p in passengers])
        self.myclients = [c for c in self.myclients if c not in self.passengers]
        return count + 1, cmd

    def exit(self, passengers):
        count, cmd = self.open()
        self.passengers = [p for p in self.passengers if p not in passengers]
        self.myclients.extend([p for p in passengers if p.end != self.floor])
        cmd = cmd or Command(self.id, 'EXIT', [p.id for p in passengers])

        return count + 1, cmd


class Call:
    def __init__(self, id, ts, start, end):
        self.id = id
        self.ts = ts
        self.start = start
        self.end = end

    def __eq__(self, other):
        if isinstance(other, Call):
            return self.id == other.id
        elif isinstance(other, int):
            return self.id == other
        else:
            return False

    def __hash__(self):
        return self.id

    def __str__(self):
        return '{{id: {}, ts: {}, start: {}, end: {}}}'.format(
            self.id, self.ts, self.start, self.end
        )

    def clone(self):
        call = Call(self.id, self.ts, self.start, self.end)
        return call


class API:
    def __init__(self):
        self.token = ''

    def start(self):
        url = '/start/{}/{}/{}'.format(USER_KEY, PROBLEM_ID, NUMBER_OF_ELEVATORS)

        result = requests.post(BASE_URL + url)

        data = result.json()
        self.token = data.get('token')

        if result.status_code != 200:
            print(result.text)

        elevators = [Elevator(i, ELEVATOR_CAPACITY, MAX_FLOOR) for i in range(NUMBER_OF_ELEVATORS)]

        for e in data['elevators']:
            el = elevators[e['id']]
            el.floor = e['floor']
            el.status = e['status']

            for p in e['passengers']:
                el.passengers(Call(p['id'], p['timestamp'], p['start'], p['end']))

        return elevators

    def oncalls(self):
        url = '/oncalls'
        headers = {
            'X-Auth-Token': self.token
        }

        result = requests.get(BASE_URL + url, headers=headers)

        if result.status_code != 200:
            print(result.text)

        data = result.json()
        calls = []
        for c in data['calls']:
            calls.append(Call(c['id'], c['timestamp'], c['start'], c['end']))

        calls = list(set(calls))

        return data['is_end'], calls

    def action(self, commands):
        url = '/action'
        headers = {
            'X-Auth-Token': self.token
        }

        result = requests.post(BASE_URL + url, headers=headers, json={
            'commands': [c.to_json() for c in commands]
        })

        if result.status_code != 200:
            print(result.text)

        return result.json()

    def score(self):
        url = '/score'
        headers = {
            'X-Auth-Token': self.token
        }

        result = requests.get(BASE_URL + url, headers=headers)

        if result.status_code != 200:
            print(result.text)

        return result.json()


class ElevatorAlgorithm:
    def __init__(self, elevators):
        self.num_elevators = len(elevators)
        self.elevators = elevators
        self.ts = 0

    def notify(self, calls):
        self.ts += 1

        for el in self.elevators:
            el.clear_clients()

        for c in calls:
            scores = [
                max(el.score()[0] if j != i else el.score_if_added(c)[0] for j, el in enumerate(self.elevators))
                for i in range(self.num_elevators)
            ]

            elidx = min(range(len(self.elevators)), key=lambda i: scores[i])
            elevator = self.elevators[elidx]
            elevator.add_client(c)

        for el in self.elevators:
            el.notify()

    def next_commands(self):
        commands = [el.next_command() for el in self.elevators]
        return commands


if __name__ == '__main__':
    api = API()

    elevators = api.start()
    algorithm = ElevatorAlgorithm(elevators)

    print('Token: ' + api.token)

    is_end, calls = api.oncalls()
    it = 0
    while not is_end and it < 10000:
        algorithm.notify(calls)
        commands = algorithm.next_commands()
        print('Command: ' + str([c.to_json() for c in commands]))
        api.action(commands)
        is_end, calls = api.oncalls()
        it += 1

    is_end, calls = api.oncalls()
    print('Result(Timestamp): ' + str(it))
    # print(api.score())
