from game.graph import get_neighbors, get_conversion_cost


def validate_route(route):
    """
    Check whether the player's route is valid.
    """

    if not isinstance(route, list) or len(route) < 2:
        return False

    for i in range(len(route) - 1):

        current_currency = route[i]
        next_currency = route[i + 1]

        neighbors = get_neighbors(current_currency)

        if next_currency not in neighbors:
            return False

    return True


def calculate_route_cost(route):
    """
    Calculate the total cost of a route.
    """

    if not validate_route(route):
        raise ValueError("Invalid route!")

    total_cost = 0

    for i in range(len(route) - 1):

        current_currency = route[i]
        next_currency = route[i + 1]

        total_cost += get_conversion_cost(
            current_currency,
            next_currency
        )

    return total_cost


def evaluate_player_route(player_route, optimal_route):
    """
    Evaluate the player's route against the optimal route.
    """

    if not validate_route(player_route):
        return {
            "valid": False,
            "cost": None,
            "optimal": False,
            "message": "Invalid route!"
        }

    player_cost = calculate_route_cost(player_route)
    optimal_cost = calculate_route_cost(optimal_route)

    return {
        "valid": True,
        "cost": player_cost,
        "optimal_cost": optimal_cost,
        "optimal": player_cost == optimal_cost,
        "difference": player_cost - optimal_cost
    }