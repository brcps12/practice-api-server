import math

import requests

BASE_URL = 'http://localhost/tbike'
# BASE_URL = 'https://kox947ka1a.execute-api.ap-northeast-2.amazonaws.com/prod/users'
PROBLEM_ID = 2

N_GRID = [5, 60][PROBLEM_ID - 1]
N_LOCATIONS = N_GRID ** 2
N_TRUCKS = [5, 10][PROBLEM_ID - 1]
N_INIT_BIKES = [4, 3][PROBLEM_ID - 1]
TRUCK_CAPACITY = 20


def id_to_xy(id):
    return id // N_GRID, id % N_GRID


def xy_to_id(x, y):
    return x * N_GRID + y


def dist(from_id, to_id):
    f_x, f_y = id_to_xy(from_id)
    t_x, t_y = id_to_xy(to_id)
    return abs(f_x - t_x) + abs(f_y - t_y)


def apx_tsp():
    pass


def get_mst(N, edges):
    parent = [-1] * N

    for c, u, v in edges:
        pu = []
        pv = []

        while parent[u] != -1:
            pu.append(u)
            u = parent[u]
        
        while parent[v] != -1:
            pv.append(v)
            v = parent[v]

        if u == v:
            continue
        
        for t in pu:
            parent[t] = v
        
        for t in pv:
            parent[t] = v
        
        parent[v] = -1

    pass


def shortest_visit_order(origin_order):
    return origin_order
    # calc mst
    edges = []
    for i in range(len(origin_order)):
        for j in range(i + 1, len(origin_order)):
            a = origin_order[i]
            b = origin_order[j]
            edges.append((dist(a, b), a, b))
    
    edges = sorted(edges)
    return origin_order


def move_command(from_id, to_id):
    commands = []
    x, y = id_to_xy(from_id)
    t_x, t_y = id_to_xy(to_id)

    while from_id != to_id and len(commands) < 10:
        if abs(x - t_x) > abs(y - t_y):
            if x < t_x:
                x += 1  # go right
                commands.append(2)
            else:
                x -= 1  # go left
                commands.append(4)
        else:
            if y < t_y:
                y += 1  # go up
                commands.append(1)
            else:
                y -= 1  # go down
                commands.append(3)
        
        from_id = xy_to_id(x, y)
    
    return commands


class Location:
    def __init__(self, id):
        self.id = id
        self.bikes_counts = []
        self.n_bikes = 0
        self.context = None

    def set_context(self, context):
        self.context = context

    def at(self, dir):
        dx = [0, 1, 0, -1]
        dy = [1, 0, -1, 0]
        x, y = id_to_xy(self.id)
        x += dx[dir - 1]
        y += dy[dir - 1]

        if not 0 <= x < N_GRID or not 0 <= y < N_GRID:
            return self
        
        return self.context.locations[xy_to_id(x, y)]


class Truck:
    def __init__(self, id):
        self.id = id
        self.bikes_count = 0
        self.location = None
        self.jobs = []
        self.context = None
        self.commands = []

    def clone(self):
        truck = Truck(self.id)
        truck.bikes_count = self.bikes_count
        truck.location = self.location
        truck.jobs.extend(self.jobs)
        truck.context = self.context

        return truck

    def set_context(self, context):
        self.context = context

    def add_job(self, job):
        # job[0]: the id of location
        # job[1]: amount of bikes for work, pos: load, neg: unload
        self.jobs.append(job)

    def clear_jobs(self):
        self.jobs = []

    def do_command(self, cmd):
        if 1 <= cmd <= 4:
            self.location = self.location.at(cmd)
        elif cmd == 5:
            # load
            if self.location.n_bikes > 0:
                self.location.n_bikes -= 1
                self.bikes_count += 1
        elif cmd == 6:
            # unload
            if self.bikes_count > 0:
                self.location.n_bikes += 1
                self.bikes_count -= 1

    def score(self):
        visit_order = [self.location.id]
        load_unload_count = 0
        for lid, c in self.jobs:
            if lid == self.location.id:
                continue
            visit_order.append(lid)
            load_unload_count += abs(c)

        visit_order = shortest_visit_order(visit_order)

        # reordering jobs
        reordered_jobs = sorted(self.jobs, key=lambda x: visit_order.index(x[0]))

        bikes_count = self.bikes_count
        cur_lid = self.location.id
        elp_time = 0

        def append_command(cmd):
            i = 0
            while len(self.commands) < 10 and i < len(cmd):
                self.commands.append(cmd[i])
                i += 1

        self.commands = []

        for lid, amount in reordered_jobs:
            if amount < 0:
                if bikes_count == 0:
                    return math.inf

                elp_time += dist(cur_lid, lid)
                append_command(move_command(cur_lid, lid))
                work_count = 0
                cur_lid = lid

                if bikes_count < -amount:
                    work_count = bikes_count
                else:
                    work_count = -amount

                elp_time += work_count
                bikes_count -= work_count
                append_command([6] * work_count)
            else:
                if bikes_count == TRUCK_CAPACITY:
                    return math.inf
            
                elp_time += dist(cur_lid, lid)
                append_command(move_command(cur_lid, lid))
                work_count = 0
                cur_lid = lid

                if bikes_count + amount > TRUCK_CAPACITY:
                    work_count = bikes_count + amount - TRUCK_CAPACITY
                else:
                    work_count = amount

                elp_time += work_count
                bikes_count += work_count
                append_command([5] * work_count)        

        return elp_time

    def score_if_added(self, job):
        truck = self.clone()
        truck.add_job(job)
        return truck.score()

    def next_command(self):
        self.score()
        return self.commands


class Context:
    def __init__(self):
        self.locations = [Location(i) for i in range(N_LOCATIONS)]
        self.trucks = [Truck(i) for i in range(N_TRUCKS)]

        for x in self.locations:
            x.set_context(self)

        for x in self.trucks:
            x.set_context(self)


class FirstAlgorithm:
    def __init__(self, context):
        self.context = context
        self.time = 0

    def next_commands(self):
        prior = [1] * N_LOCATIONS

        for loc in self.context.locations:
            if loc.bikes_counts[-1] == 0:
                prior[loc.id] *= 1.7
            elif loc.bikes_counts[-1] <= 1:
                prior[loc.id] *= 1.5
            elif loc.bikes_counts[-1] >= 4:
                prior[loc.id] *= 1.7
            elif loc.bikes_counts[-1] >= 2:
                prior[loc.id] *= 1.5

        pi = sorted(enumerate(prior), key=lambda x: x[1], reverse=True)

        work_type = [0] * N_LOCATIONS

        for i in range(N_LOCATIONS):
            c = self.context.locations[i].bikes_counts[-1]
            if c == 0:
                work_type[i] = -2
            elif c <= 1:
                work_type[i] = -1
            elif c >= 2:
                work_type[i] = c - 1

        jobs = []
        for i in range(25):
            lid = pi[i][0]
            jobs.append((lid, work_type[lid]))
            
        print(jobs[:10])

        for truck in self.context.trucks:
            truck.clear_jobs()

        for job in jobs:
            scores_added = [truck.score_if_added(job) for truck in self.context.trucks]
            k = min(range(N_TRUCKS), key=lambda x: scores_added[x])
            if scores_added[k] == math.inf:
                continue
            self.context.trucks[k].add_job(job)

        commands = [self.context.trucks[i].next_command() for i in range(N_TRUCKS)]
        
        self.time += 1

        return [{'truck_id': i, 'command': commands[i]} for i in range(N_TRUCKS)]


class SecondAlgorithm:
    def __init__(self, context):
        self.context = context
        self.time = 0
        self.op_diffs = [[0] for _ in range(N_LOCATIONS)]
        self.last_work_info = [0] * N_LOCATIONS

    def next_commands(self):
        # Calculate how amount of requests and returns are occurred
        for i in range(N_LOCATIONS):
            loc = self.context.locations[i]
            diff = loc.bikes_counts[-1] - loc.bikes_counts[-2] + self.last_work_info[loc.id]
            self.op_diffs[i].append(diff + self.op_diffs[i][-1])
        
        # recent 4 hours
        base = max(self.time - 50, 0)
        trends = [(v[-1] - v[base], i) for i, v in enumerate(self.op_diffs)]
        trends = sorted(trends)

        prior = [1] * N_LOCATIONS
        
        for i in range(N_LOCATIONS // 2):
            lid = trends[i][1]
            p = 5 * (1 / (1 + math.exp(8 * i / (N_LOCATIONS // 2) - 4)))
            prior[lid] *= p

            lid = trends[-i - 1][1]
            p = 5 * (1 / (1 + math.exp(8 * i / (N_LOCATIONS // 2) - 4)))
            prior[lid] *= p

        for loc in self.context.locations:
            if loc.bikes_counts[-1] == 0:
                prior[loc.id] *= 1.7
            elif loc.bikes_counts[-1] <= 1:
                prior[loc.id] *= 1.5
            elif loc.bikes_counts[-1] >= 7:
                prior[loc.id] *= 1.7
            elif loc.bikes_counts[-1] >= 4:
                prior[loc.id] *= 1.5

        pi = sorted(enumerate(prior), key=lambda x: x[1], reverse=True)

        avg_bikes = 0
        for loc in self.context.locations:
            avg_bikes += loc.n_bikes
        for truck in self.context.trucks:
            avg_bikes += truck.bikes_count
        avg_bikes /= N_LOCATIONS

        print('avg_bikes: ' + str(avg_bikes))

        # top 1000 locations are working

        # need work type, pos: load to truck, neg: unload from truck, 0: nothing
        work_type = [0] * N_LOCATIONS

        for i in range(N_LOCATIONS):
            c = self.context.locations[i].bikes_counts[-1]
            if c == 0:
                work_type[i] = -2
            elif c <= 1:
                work_type[i] = -1
            elif c >= 4:
                work_type[i] = c - 2

        for c, lid in trends:
            avg = (self.op_diffs[lid][-1] - self.op_diffs[lid][base]) / ((self.time - base) or 1)
            
            if c > 5 and self.context.locations[lid].bikes_counts[-1] >= 2:
                work_type[lid] = self.context.locations[lid].bikes_counts[-1] - 2
            elif c < -5 and self.context.locations[lid].bikes_counts[-1] <= 7:
                work_type[lid] = self.context.locations[lid].bikes_counts[-1] - 7 - 1

        def all_jobs():
            for lid, _ in pi:
                if work_type[lid] != 0:
                    yield (lid, work_type[lid])

        for truck in self.context.trucks:
            truck.clear_jobs()

        jobs = list(all_jobs())
        before_jobs = 0

        succ = 0
        for job in all_jobs():
            scores_added = [truck.score_if_added(job) for truck in self.context.trucks]
            k = min(range(N_TRUCKS), key=lambda x: scores_added[x])
            if scores_added[k] == math.inf:
                continue
            self.context.trucks[k].add_job(job)
            succ += 1

            if succ >= 100:
                break

        commands = [self.context.trucks[i].next_command() for i in range(N_TRUCKS)]
        print(jobs[:10])

        for i in range(N_LOCATIONS):
            self.last_work_info[i] = 0

        for i in range(10):
            for j in range(N_TRUCKS):
                truck = self.context.trucks[j]

                if i >= len(commands[j]):
                    continue

                cmd = commands[j][i]
                truck.do_command(cmd)
                if cmd == 5:
                    self.last_work_info[truck.location.id] += 1
                elif cmd == 6:
                    self.last_work_info[truck.location.id] -= 1
        
        self.time += 1

        return [{'truck_id': i, 'command': commands[i]} for i in range(N_TRUCKS)]


class API:
    def __init__(self):
        self.token = ''

    def start(self):
        url = '/start'
        headers = {
            'X-Auth-Token': '919a5e6cda280d3de55fbad80c5b2897'
        }

        result = requests.post(BASE_URL + url, headers=headers, json={
            'problem': PROBLEM_ID
        })

        if result.status_code != 200:
            print(result.text)

        data = result.json()
        self.token = data.get('auth_key')

    def locations(self, context):
        url = '/locations'
        headers = {
            'Authorization': self.token
        }

        result = requests.get(BASE_URL + url, headers=headers)

        if result.status_code != 200:
            print(result.text)

        data = result.json()

        for item in data['locations']:
            loc = context.locations[item['id']]
            loc.bikes_counts.append(item['located_bikes_count'])
            loc.n_bikes = item['located_bikes_count']
            

    def trucks(self, context):
        url = '/trucks'
        headers = {
            'Authorization': self.token
        }

        result = requests.get(BASE_URL + url, headers=headers)

        if result.status_code != 200:
            print(result.text)

        data = result.json()

        for item in data['trucks']:
            truck = context.trucks[item['id']]

            truck.location = context.locations[item['location_id']]

            # assert truck.location.id == item['location_id'], 'Truck ID: ' + str(truck.id) + ' Current: ' + str(truck.location.id) + ', but server: ' + str(item['location_id'])
            # assert truck.bikes_count == item['loaded_bikes_count'], 'Truck ID: ' + str(truck.id) + ', Current: ' + str(truck.bikes_count) + ', but server: ' + str(item['loaded_bikes_count'])
            # continue
            truck.bikes_count = item['loaded_bikes_count']

    def simulate(self, commands):
        url = '/simulate'
        headers = {
            'Authorization': self.token
        }

        result = requests.put(BASE_URL + url, headers=headers, json={
            'commands': commands
        })

        if result.status_code != 200:
            print(result.text)

        return result.json()

    def score(self):
        url = '/score'
        headers = {
            'Authorization': self.token
        }

        result = requests.get(BASE_URL + url, headers=headers)

        if result.status_code != 200:
            print(result.text)

        return result.json()


if __name__ == '__main__':
    context = Context()
    algo = FirstAlgorithm(context) if PROBLEM_ID == 1 else SecondAlgorithm(context)

    api = API()
    api.start()
    print('Token: ' + api.token)

    api.locations(context)
    api.trucks(context)

    t = 0
    while t < 12 * 60:
        api.locations(context)
        api.trucks(context)

        commands = algo.next_commands()
        print(api.simulate(commands))

        print('TS: ' + str(t)) # + ', Commands: ' + json.dumps(commands))
        t += 1

    print(api.score())
