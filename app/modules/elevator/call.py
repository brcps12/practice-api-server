class Call:
    def __init__(self, id, timestamp, start, end):
        self.id = id
        self.timestamp = timestamp
        self.start = start
        self.end = end
    
    def to_json(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'start': self.start,
            'end': self.end
        }
