class TBikeTruck:
    def __init__(self, id, capacity, init_location):
        self.id = id
        self.capacity = capacity
        self.location = init_location
        self.bikes_count = 0
        self.distance = 0

    def to_json(self):
        return {
            'id': self.id,
            'location_id': self.location.id,
            'loaded_bikes_count': self.bikes_count
        }

    def go_top(self):
        loc = self.location.at_top()
        if loc is not None:
            self.location = loc
            self.distance += 1

    def go_down(self):
        loc = self.location.at_down()
        if loc is not None:
            self.location = loc
            self.distance += 1

    def go_left(self):
        loc = self.location.at_left()
        if loc is not None:
            self.location = loc
            self.distance += 1

    def go_right(self):
        loc = self.location.at_right()
        if loc is not None:
            self.location = loc
            self.distance += 1

    def load_bike(self):
        if self.location.bikes_count > 0 and self.bikes_count < self.capacity:
            self.location.bikes_count -= 1
            self.bikes_count += 1

    def unload_bike(self):
        if self.bikes_count > 0:
            self.location.bikes_count += 1
            self.bikes_count -= 1
