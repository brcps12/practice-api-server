from app.modules.elevator.elevator import Elevator


class ElevatorContext:
    def __init__(self, problem_id, number_of_elevators):
        self.problem_id = problem_id
        self.number_of_elevators = number_of_elevators

        self.elevators = []
        self.calls = []
        self.timestamp = 0
        self.is_end = False

        for _ in range(number_of_elevators):
            self.new_elevator()

    def new_elevator(self):
        id = len(self.elevators)
        elevator = Elevator(id)
        self.elevators.append(elevator)
        return elevator

    def stop(self, elevator_id):
        pass
    
    def open(self, elevator_id):
        pass
    
    def close(self, elevator_id):
        pass
    
    def enter(self, elevator_id, call_ids):
        pass
    
    def exit(self, elevator_id, call_ids):
        pass
    
    def up(self, elevator_id):
        pass
    
    def down(self, elevator_id):
        pass
    