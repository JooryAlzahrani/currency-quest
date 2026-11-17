import math

import plotly.graph_objects as go


# Plot colors (same as the interface colors in app.py)
GOLD = "#E9B949"
GREEN = "#3DD68C"
NODE = "#1E2A44"
TEXT = "#E8ECF4"
EDGE = "rgba(138,147,166,0.35)"


# Plot colors (same as the interface colors in app.py)
def node_positions(currencies):
    positions = {}
    for i, code in enumerate(currencies):
        angle = math.pi / 2 - 2 * math.pi * i / len(currencies)
        positions[code] = (math.cos(angle), math.sin(angle))
    return positions


# Draws the currencies explored by A* with their exploration order, and the optimal route
def make_astar_figure(graph, result):
    currencies = list(graph)
    pos = node_positions(currencies)
    path = result["path"] or []
    path_edges = {tuple(sorted(e)) for e in zip(path, path[1:])}
    order = {c: i + 1 for i, c in enumerate(result["explored"])}

    fig = go.Figure()

    drawn = set()
    label_x, label_y, label_text = [], [], []
    for source, edges in graph.items():
        for target, weight in edges.items():
            key = tuple(sorted((source, target)))
            if key in drawn:
                continue
            drawn.add(key)
            (x0, y0), (x1, y1) = pos[key[0]], pos[key[1]]
            on_path = key in path_edges
            fig.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1], mode="lines", hoverinfo="skip", showlegend=False,
                line=dict(color=GREEN if on_path else EDGE, width=6 if on_path else 2),
            ))
            label_x.append(x0 + 0.4 * (x1 - x0))
            label_y.append(y0 + 0.4 * (y1 - y0))
            label_text.append(str(weight))

    fig.add_trace(go.Scatter(
        x=label_x, y=label_y, mode="text", text=label_text,
        textfont=dict(color=TEXT, size=13), hoverinfo="skip", showlegend=False,
    ))

    colors = [GREEN if c in path else GOLD if c in order else NODE for c in currencies]
    labels = [f"<b>{c}</b><br>#{order[c]}" if c in order else c for c in currencies]
    fig.add_trace(go.Scatter(
        x=[pos[c][0] for c in currencies], y=[pos[c][1] for c in currencies],
        mode="markers+text", text=labels, textposition="middle center",
        textfont=dict(color=["#111" if c in order else TEXT for c in currencies], size=13),
        marker=dict(size=56, color=colors, line=dict(color=GOLD, width=2)),
        hoverinfo="skip", showlegend=False,
    ))

    fig.update_layout(
        title=dict(
            text=f"A*: {' → '.join(path)}  |  cost = {result['cost']}  |  explored = {len(result['explored'])}",
            x=0.5, font=dict(color=TEXT),
        ),
        height=450, margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, range=[-1.3, 1.3]),
        yaxis=dict(visible=False, range=[-1.3, 1.3], scaleanchor="x"),
    )
    return fig



