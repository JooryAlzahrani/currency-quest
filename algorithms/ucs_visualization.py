
import plotly.graph_objects as go


def visualize_ucs(graph, result):

    positions = {
        "SAR": (0, 2),
        "USD": (2, 3),
        "EUR": (4, 3),
        "GBP": (6, 2),
        "JPY": (4, 0),
        "AED": (2, 0)
    }

    path = result["path"]
    explored = set(result["explored_nodes"])
    path_edges = set(zip(path, path[1:]))

    fig = go.Figure()

    # Draw graph edges
    for source, neighbors in graph.items():
        for target, cost in neighbors.items():

            # Avoid drawing reciprocal edges twice
            if source < target:
                x1, y1 = positions[source]
                x2, y2 = positions[target]

                is_path_edge = (
                    (source, target) in path_edges or
                    (target, source) in path_edges
                )

                fig.add_trace(go.Scatter(
                    x=[x1, x2],
                    y=[y1, y2],
                    mode="lines",
                    line=dict(
                        color="green" if is_path_edge else "lightgray",
                        width=4 if is_path_edge else 2
                    ),
                    hoverinfo="text",
                    text=f"{source} → {target}: {cost}",
                    showlegend=False
                ))

                fig.add_annotation(
                    x=(x1 + x2) / 2,
                    y=(y1 + y2) / 2,
                    text=str(cost),
                    showarrow=False,
                    bgcolor="white"
                )

    # Draw currency nodes
    node_colors = [
        "green" if currency in path else
        "orange" if currency in explored else
        "lightblue"
        for currency in graph
    ]

    fig.add_trace(go.Scatter(
        x=[positions[c][0] for c in graph],
        y=[positions[c][1] for c in graph],
        mode="markers+text",
        text=list(graph.keys()),
        textposition="top center",
        marker=dict(
            size=35,
            color=node_colors,
            line=dict(width=1, color="black")
        ),
        showlegend=False
    ))

    fig.update_layout(
        title="Uniform Cost Search - Optimal Route",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        template="plotly_white",
        height=500
    )

    return fig
