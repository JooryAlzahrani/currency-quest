import heapq
import time

from algorithms.heuristic import build_heuristic


# Finds the minimum-cost route from start to goal using f(n) = g(n) + h(n)
def astar_search(graph, start, goal):
    t0 = time.perf_counter()
    h = build_heuristic(graph, goal)

    g = {start: 0}
    parent = {start: None}
    counter = 0
    frontier = [(h[start], counter, start)]
    closed = set()
    explored = []

    while frontier:
        _, _, node = heapq.heappop(frontier)
        if node in closed:
            continue
        closed.add(node)
        explored.append(node)

        if node == goal:
            break

        for nbr, cost in graph[node].items():
            if nbr in closed:
                continue
            new_g = g[node] + cost
            if new_g < g.get(nbr, float("inf")):
                g[nbr] = new_g
                parent[nbr] = node
                counter += 1
                heapq.heappush(frontier, (new_g + h[nbr], counter, nbr))

    elapsed = time.perf_counter() - t0

    if goal not in closed:
        path, cost = None, None
    else:
        path, node = [], goal
        while node is not None:
            path.append(node)
            node = parent[node]
        path.reverse()
        cost = g[goal]

    return {
        "path": path,
        "cost": cost,
        "explored": explored,
        "time": elapsed,
    }