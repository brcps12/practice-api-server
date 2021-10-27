from app.modules.elevator.call import Call
from app.modules.elevator.erros import CommandError


class Elevator:
    def __init__(self, id, capacity, max_floor):
        self.id = id
        self.capacity = capacity
        self.max_floor = max_floor

        self.floor = 1
        self.passengers = []
        self.status = 'STOPPED'

    def to_json(self):
        return {
            'id': self.id,
            'floor': self.floor,
            'passengers': [call.to_json() for call in self.passengers],
            'status': self.status
        }

    def stop(self):
        if self.status not in ['STOPPED', 'UPWARD', 'DOWNWARD']:
            raise CommandError()
        
        self.status = 'STOPPED'
    
    def open(self):
        if self.status not in ['STOPPED', 'OPENED']:
            raise CommandError()

        self.status = 'OPENED'
    
    def close(self):
        if self.status not in ['OPENED']:
            raise CommandError()

        self.status = 'STOPPED'
    
    def enter(self, passengers):
        if self.status not in ['OPENED']:
            raise CommandError()

        for p in passengers:
            if p.start != self.floor:
                raise CommandError()

        if len(self.passengers) + len(passengers) > self.capacity:
            raise CommandError('4')

        self.passengers.extend(passengers)

        self.status = 'OPENED'
    
    def exit(self, passenger_ids):
        if self.status not in ['OPENED']:
            raise CommandError()

        passengers = self.passengers

        self.passengers = []
        exit_passengers = []

        for p in passengers:
            if p.id in passenger_ids:
                exit_passengers.append(p)
            else:
                self.passengers.append(p)

        if len(exit_passengers) != len(passenger_ids):
            raise CommandError()

        self.status = 'OPENED'

        return exit_passengers
    
    def up(self):
        if self.status not in ['STOPPED', 'UPWARD']:
            raise CommandError()

        if self.floor == self.max_floor:
            raise CommandError()
        
        self.floor += 1
        self.status = 'UPWARD'
    
    def down(self):
        if self.status not in ['STOPPED', 'DOWNWARD']:
            raise CommandError()

        if self.floor == 1:
            raise CommandError()

        self.floor -= 1
        self.status = 'DOWNWARD'
        
