from collections import deque

# Returns the cheapest conversion cost in the whole graph
def min_edge_cost(graph):
    return min(w for nbrs in graph.values() for w in nbrs.values())

# Computes the minimum number of conversions from each currency to the goal using BFS
def hop_distances_to(graph, goal):
    reverse = {n: [] for n in graph}
    for a, nbrs in graph.items():
        for b in nbrs:
            reverse.setdefault(b, []).append(a)

    hops = {goal: 0}
    queue = deque([goal])
    while queue:
        node = queue.popleft()
        for prev in reverse.get(node, []):
            if prev not in hops:
                hops[prev] = hops[node] + 1
                queue.append(prev)
    return hops

# Computes h for each currency: the maximum of three estimates that never exceed the true cost
def build_heuristic(graph, goal):
    w_min = min_edge_cost(graph)
    hops = hop_distances_to(graph, goal)
    incoming = [nbrs[goal] for nbrs in graph.values() if goal in nbrs]
    arrive = min(incoming) if incoming else float("inf")

    h = {}
    for node in graph:
        if node == goal:
            h[node] = 0.0
        elif node not in hops:
            h[node] = float("inf")
        else:
            hop_bound = hops[node] * w_min
            leave = min(graph[node].values()) if graph[node] else float("inf")
            h[node] = max(hop_bound, leave, arrive)
    return h

# Computes the true minimum cost from each currency to the goal (for testing only, not used by A*)
def true_costs_to(graph, goal):
    import heapq
    reverse = {n: {} for n in graph}
    for a, nbrs in graph.items():
        for b, w in nbrs.items():
            reverse.setdefault(b, {})[a] = w
    dist = {goal: 0.0}
    pq = [(0.0, goal)]
    while pq:
        d, node = heapq.heappop(pq)
        if d > dist.get(node, float("inf")):
            continue
        for prev, w in reverse[node].items():
            nd = d + w
            if nd < dist.get(prev, float("inf")):
                dist[prev] = nd
                heapq.heappush(pq, (nd, prev))
    return dist

# Checks that the heuristic never exceeds the true cost for any currency (admissibility)
def is_admissible(graph, goal, h=None):
    h = h or build_heuristic(graph, goal)
    true = true_costs_to(graph, goal)
    return all(h[n] <= true.get(n, float("inf")) + 1e-9 for n in graph)

# Checks that the heuristic never underestimates the true cost for any currency (consistency)
def is_consistent(graph, goal, h=None):
    h = h or build_heuristic(graph, goal)
    return all(
        h[n] <= w + h[m] + 1e-9
        for n, nbrs in graph.items() for m, w in nbrs.items()
    )



