from game.game_logic import (
    validate_route,
    calculate_route_cost,
    evaluate_player_route
)


def test_valid_route():
    route = ["USD", "EUR"]

    result = validate_route(route)

    print("Valid Route Test:", result)


def test_invalid_route():
    route = ["USD", "INVALID"]

    result = validate_route(route)

    print("Invalid Route Test:", result)


def test_route_cost():
    route = ["USD", "EUR"]

    if validate_route(route):
        print("Route Cost Test:", calculate_route_cost(route))
    else:
        print("Cannot calculate cost: Invalid route")


def test_player_evaluation():
    player_route = ["USD", "EUR"]
    optimal_route = ["USD", "EUR"]

    result = evaluate_player_route(player_route, optimal_route)

    print("Player Evaluation Test:", result)


if __name__ == "__main__":

    print("===== Currency Quest Tests =====")

    test_valid_route()
    test_invalid_route()
    test_route_cost()
    test_player_evaluation()