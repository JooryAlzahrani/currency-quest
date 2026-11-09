
from game.graph import graph
from algorithms.ucs import ucs


def test_direct_route():
    result = ucs(graph, "USD", "EUR")

    print("Direct Route Test:", result["path"])
    print("Total Cost:", result["total_cost"])


def test_optimal_route():
    result = ucs(graph, "SAR", "GBP")

    print("Optimal Route Test:", result["path"])
    print("Total Cost:", result["total_cost"])


def test_explored_nodes():
    result = ucs(graph, "SAR", "JPY")

    print("Explored Nodes:", result["explored_nodes"])
    print("Number of Explored Nodes:", result["explored_count"])


def test_execution_time():
    result = ucs(graph, "AED", "EUR")

    print("Execution Time:", result["execution_time"], "seconds")


def test_unreachable_route():
    test_graph = {
        "SAR": {"USD": 4},
        "USD": {"SAR": 4},
        "EUR": {}
    }

    result = ucs(test_graph, "SAR", "EUR")

    print("Unreachable Route Test:", result["path"])
    print("Total Cost:", result["total_cost"])


if __name__ == "__main__":

    print("===== UCS Tests =====")

    test_direct_route()
    test_optimal_route()
    test_explored_nodes()
    test_execution_time()
    test_unreachable_route()
