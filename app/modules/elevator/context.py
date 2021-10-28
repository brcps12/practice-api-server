from app.modules.elevator.call import Call
from app.modules.elevator.dataset import load_dataset
from app.modules.elevator.elevator import Elevator
from app.modules.elevator.erros import CommandError


command_short = {
    'STOP': 'S',
    'OPEN': 'O',
    'CLOSE': 'C',
    'UP': 'U',
    'DOWN': 'D',
    'ENTER': 'E',
    'EXIT': 'X'
}

status_short = {
    'STOPPED': 'S',
    'OPENED': 'O',
    'UPWARD': 'U',
    'DOWNWARD': 'D'
}

MAX_NUM_ELEVATORS = 4

class ElevatorContext:
    def __init__(self, problem_id, number_of_elevators):
        self.problem_id = problem_id
        self.number_of_elevators = number_of_elevators

        self.elevators = []
        self.calls = []
        self.timestamp = -1
        self.is_end = False
        self.finish_calls = 0

        if problem_id == 0:
            self.capacity = 8
            self.max_floor = 6
            self.max_number_of_calls = 6
        elif problem_id == 1:
            self.capacity = 8
            self.max_floor = 25
            self.max_number_of_calls = 200
        else:
            self.capacity = 8
            self.max_floor = 25
            self.max_number_of_calls = 500

        self.dataset = load_dataset(self.problem_id)
        self.dataset_lookup = 0
        self.history = []

        self.tick()

        for _ in range(number_of_elevators):
            self.new_elevator()

    def _make_empty_history(self):
        elevators = [{
            "floor": 0,
            "state": "",
            "command": "",
            "passengers": []
        } for _ in range(MAX_NUM_ELEVATORS)]

        self.history.append({'elevators': elevators, 'calls': []})

    def _call_to_history(self, call):
        return {
            'id': call.id,
            'from': call.start,
            'to': call.end
        }

    def _write_elevator_history(self, id, cmd):
        el = self.elevators[id]
        hist = self.history[-1]['elevators'][id]
        hist['floor'] = el.floor
        hist['command'] = cmd
        hist['state'] = status_short[el.status]
        hist['passengers'] = [self._call_to_history(c) for c in el.passengers]

    def _write_call_history(self):
        hist = self.history[-1]['calls']
        hist.extend([self._call_to_history(c) for c in self.calls])

    def new_elevator(self):
        id = len(self.elevators)
        
        elevator = Elevator(id, self.capacity, self.max_floor)
        self.elevators.append(elevator)
        self._write_elevator_history(id, 'S')
        return elevator

    def tick(self):
        self.timestamp += 1

        while self.dataset_lookup < len(self.dataset):
            item = self.dataset[self.dataset_lookup]

            if item[0] > self.timestamp:
                break

            call = Call(item[1], item[0], item[2], item[3])
            self.calls.append(call)
            self.dataset_lookup += 1
        
        if self.finish_calls == len(self.dataset):
            self.is_end = True

        self._make_empty_history()
        self._write_call_history()

    def stop(self, elevator_id):
        self.elevators[elevator_id].stop()
        self._write_elevator_history(elevator_id, 'S')
    
    def open(self, elevator_id):
        self.elevators[elevator_id].open()
        self._write_elevator_history(elevator_id, 'O')
    
    def close(self, elevator_id):
        self.elevators[elevator_id].close()
        self._write_elevator_history(elevator_id, 'C')
    
    def enter(self, elevator_id, call_ids):
        calls = self.calls

        self.calls = []
        filtered = []

        for c in calls:
            if c.id in call_ids:
                filtered.append(c)
            else:
                self.calls.append(c)

        if len(filtered) != len(call_ids):
            raise CommandError()

        self.elevators[elevator_id].enter(filtered)
        self._write_elevator_history(elevator_id, 'E')
    
    def exit(self, elevator_id, call_ids):
        elevator = self.elevators[elevator_id]
        calls = elevator.exit(call_ids)
        self.finish_calls += len(calls)

        calls = [c for c in calls if c.end != elevator.floor]
        self.finish_calls -= len(calls)

        for c in calls:
            c.timestamp = self.timestamp
            c.start = elevator.floor
            self.calls.append(c)

        self._write_elevator_history(elevator_id, 'X')
    
    def up(self, elevator_id):
        self.elevators[elevator_id].up()
        self._write_elevator_history(elevator_id, 'U')
    
    def down(self, elevator_id):
        self.elevators[elevator_id].down()
        self._write_elevator_history(elevator_id, 'D')
    