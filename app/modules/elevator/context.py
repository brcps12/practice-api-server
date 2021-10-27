from app.modules.elevator.call import Call
from app.modules.elevator.dataset import load_dataset
from app.modules.elevator.elevator import Elevator
from app.modules.elevator.erros import CommandError


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

        self.tick()

        for _ in range(number_of_elevators):
            self.new_elevator()

    def new_elevator(self):
        id = len(self.elevators)
        
        elevator = Elevator(id, self.capacity, self.max_floor)
        self.elevators.append(elevator)
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

    def stop(self, elevator_id):
        self.elevators[elevator_id].stop()
    
    def open(self, elevator_id):
        self.elevators[elevator_id].open()
    
    def close(self, elevator_id):
        self.elevators[elevator_id].close()
    
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
    
    def up(self, elevator_id):
        self.elevators[elevator_id].up()
    
    def down(self, elevator_id):
        self.elevators[elevator_id].down()
    