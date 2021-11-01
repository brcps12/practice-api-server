import json
from os import path


def get_raw_json(filename):
    with open(filename) as f:
        return json.loads(f.read())


def load_dataset(problem):
    filename = path.join(path.dirname(__file__), 'data/problem{}_day-3.json'.format(problem))

    reqs = [[] for _ in range(12 * 60)]
    data = get_raw_json(filename)

    for k, v in data.items():
        reqs[int(k)] = v

    return reqs
