# empty file
import heapq
import time

def ucs(graph, start, goal):
    start_time = time.perf_counter()

    if start not in graph or goal not in graph:
        raise ValueError("Invalid starting or target currency.")

    # Priority queue: (accumulated cost, current node, path)
    priority_queue = [(0, start, [start])]

    # Lowest known cost to reach each currency
    best_cost = {start: 0}

    explored_nodes = []

    while priority_queue:
        current_cost, current, path = heapq.heappop(priority_queue)

        # Skip outdated entries
        if current_cost > best_cost[current]:
            continue

        # Expand the node
        explored_nodes.append(current)

        # Goal test when removed from the priority queue
        if current == goal:
            return {
                "path": path,
                "total_cost": current_cost,
                "explored_nodes": explored_nodes,
                "explored_count": len(explored_nodes),
                "execution_time": time.perf_counter() - start_time
            }

        # Expand neighboring currencies
        for neighbor, edge_cost in graph[current].items():
            new_cost = current_cost + edge_cost

            if new_cost < best_cost.get(neighbor, float("inf")):
                best_cost[neighbor] = new_cost

                heapq.heappush(
                    priority_queue,
                    (new_cost, neighbor, path + [neighbor])
                )

    return {
        "path": [],
        "total_cost": float("inf"),
        "explored_nodes": explored_nodes,
        "explored_count": len(explored_nodes),
        "execution_time": time.perf_counter() - start_time
    }
