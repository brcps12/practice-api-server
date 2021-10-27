from app.modules.elevator.call import Call


class Elevator:
    def __init__(self, id=0):
        self.id = id
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
