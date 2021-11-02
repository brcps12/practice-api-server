from .dataset import load_dataset
from .location import TBikeLocation
from .truck import TBikeTruck

NUMBER_OF_GRID = [5, 60]
NUMBER_OF_TRUCKS = [5, 10]
NUMBER_OF_BIKES_IN_EACH_LOCATION = [4, 3]
TRUCK_CAPACITY = 20
TOTAL_TIMES = 12 * 60  # 12 hours


class TBikeSystem:
    def __init__(self, problem):
        self.problem = problem
        self.time = 0
        self.success_requests_count = 0
        self.failed_requests_count = 0
        self.status = 'ready'

        self.grid = NUMBER_OF_GRID[problem - 1]
        self.init_bikes_count = NUMBER_OF_BIKES_IN_EACH_LOCATION[problem - 1]
        self.locations = [TBikeLocation(i, self.init_bikes_count) for i in range(self.grid ** 2)]

        for loc in self.locations:
            loc.set_location_map(self.grid, self.locations)

        self.trucks = [TBikeTruck(i, TRUCK_CAPACITY, self.locations[0]) for i in range(NUMBER_OF_TRUCKS[problem - 1])]

        self.bikes_requests = load_dataset(problem)
        self.bikes_returns = [[] for _ in range(TOTAL_TIMES)]

    def before_simulate(self):
        rets = self.bikes_returns[self.time]
        for lid in rets:
            self.locations[lid].bike_return()

        reqs = self.bikes_requests[self.time]
        for from_lid, to_lid, dura in reqs:
            if not self.locations[from_lid].bike_request():
                self.failed_requests_count += 1
            else:
                self.success_requests_count += 1

                if self.time + dura < len(self.bikes_returns):
                    self.bikes_returns[self.time + dura].append(to_lid)

    def simulate(self, commands):
        self.status = 'in_progress'

        self.before_simulate()

        truck_cmds = []

        for truck in self.trucks:
            cmds = []
            for item in commands:
                if item['truck_id'] == truck.id:
                    cmds = item['command']
                    break
            truck_cmds.append(cmds)

        for sec in range(10):
            for truck, cmds in zip(self.trucks, truck_cmds):
                if sec >= len(cmds):
                    continue

                c = int(cmds[sec])

                if c == 1:
                    truck.go_up()
                elif c == 2:
                    truck.go_right()
                elif c == 3:
                    truck.go_down()
                elif c == 4:
                    truck.go_left()
                elif c == 5:
                    truck.load_bike()
                elif c == 6:
                    truck.unload_bike()
                else:
                    None

        self.status = 'ready'
        self.time += 1
        distance = 0

        for truck in self.trucks:
            distance += truck.distance

        if self.time >= 720:
            self.status = 'finished'

        return {
            'status': self.status,
            'time': self.time,
            'failed_requests_count': self.failed_requests_count,
            'distance': distance / 10
        }
