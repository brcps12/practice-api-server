class Call:
    def __init__(self, id):
        self.id = id
        self.timestamp = 0
        self.start = 0
        self.end = 0
    
    def to_json(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'start': self.start,
            'end': self.end
        }
