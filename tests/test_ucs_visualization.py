
from game.graph import graph
from algorithms.ucs import ucs
from algorithms.ucs_visualization import visualize_ucs

# Run UCS
result = ucs(graph, "SAR", "GBP")

# Generate visualization
fig = visualize_ucs(graph, result)

# Open visualization in browser
fig.show()
