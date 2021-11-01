class TBikeLocation:
    def __init__(self, id, init_bikes_count=0):
        self.id = id
        self.bikes_count = init_bikes_count

        self.number_of_grid = 0
        self.location_map = None

    def to_json(self):
        return {
            'id': self.id,
            'located_bikes_count': self.bikes_count
        }

    def set_location_map(self, number_of_grid, location_map):
        self.number_of_grid = number_of_grid
        self.location_map = location_map

    def _get_relative_location(self, dx, dy):
        x, y = self.id // self.number_of_grid, self.id % self.number_of_grid
        x += dx
        y += dy
        id = x * self.number_of_grid + y

        if not 0 <= x < self.number_of_grid or not 0 <= y < self.number_of_grid:
            return None
        return self.location_map[id]

    def at_top(self):
        return self._get_relative_location(0, 1)

    def at_down(self):
        return self._get_relative_location(0, -1)

    def at_left(self):
        return self._get_relative_location(-1, 0)

    def at_right(self):
        return self._get_relative_location(1, 0)

    def bike_return(self):
        self.bikes_count += 1
        return True

    def bike_request(self):
        if self.bikes_count <= 0:
            return False

        self.bikes_count -= 1
        return True
