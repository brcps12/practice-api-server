def eval_tbike(tbike):
    if tbike.status != 'finished':
        return 0

    S = 0
    Sp = 0

    bikes = [tbike.init_bikes_count for _ in range(len(tbike.locations))]
    bike_returns = [[] for _ in range(len(tbike.bikes_requests))]

    for t, reqs in enumerate(tbike.bikes_requests):
        rets = bike_returns[t]
        for lid in rets:
            bikes[lid] += 1

        for flid, tlid, dura in reqs:
            S += 1
            if bikes[flid] > 0:
                bikes[flid] -= 1
                if t + dura < len(bike_returns):
                    bike_returns[t + dura].append(tlid)
                Sp += 1

    S1 = (tbike.success_requests_count - Sp) / (S - Sp) * 100

    T = len(tbike.trucks) * len(tbike.bikes_requests)
    t = 0
    for truck in tbike.trucks:
        t += truck.distance / 10

    S2 = (T - t) / T * 100

    print(S1, S2)
    print(tbike.success_requests_count, S, Sp)
    print(T, t)
    return max(S1 * 0.95 + S2 * 0.05, 0)
