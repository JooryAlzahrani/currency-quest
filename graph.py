# graph.py

# Available currencies in the game
currencies = ["SAR", "USD", "EUR", "GBP", "JPY", "AED"]


# Weighted Directed Graph
# Each edge represents an available currency conversion.
# Each weight represents a simulated conversion cost.
# All weights are non-negative.

graph = {
    "SAR": {
        "USD": 4,
        "EUR": 7,
        "AED": 2
    },

    "USD": {
        "SAR": 4,
        "EUR": 3,
        "GBP": 6,
        "JPY": 8
    },

    "EUR": {
        "SAR": 7,
        "USD": 3,
        "GBP": 2,
        "AED": 5
    },

    "GBP": {
        "USD": 6,
        "EUR": 2,
        "JPY": 4
    },

    "JPY": {
        "USD": 8,
        "GBP": 4,
        "AED": 6
    },

    "AED": {
        "SAR": 2,
        "EUR": 5,
        "JPY": 6
    }
}


# Return available neighboring currencies
def get_neighbors(currency):
    return graph.get(currency, {})


# Return the cost of a direct conversion
def get_conversion_cost(source, target):
    return graph.get(source, {}).get(target)


# Display the graph
if __name__ == "__main__":

    print("Currency Quest - Currency Graph")
    print("-" * 40)

    for currency, connections in graph.items():
        print(f"\n{currency}:")

        for target, cost in connections.items():
            print(f"  {currency} -> {target}: Cost = {cost}")

    print("\nTotal currencies:", len(currencies))

    total_edges = sum(len(connections) for connections in graph.values())

    print("Total conversions:", total_edges)