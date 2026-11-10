"""
Currency Quest - Streamlit interface (Person 4).

Run with:  streamlit run app.py

Connects the interface to:
  - game/graph.py        (currencies + weighted graph)
  - game/game_logic.py   (route validation, cost, player evaluation)
  - algorithms/ucs.py    (Uniform Cost Search)
  - algorithms/astar.py  (A* Search)

Expected algorithm interface (agree on this with the UCS / A* owners):
    uniform_cost_search(graph, start, goal) -> {
        "path": [...], "cost": int, "explored": [...], "time": seconds
    }
    astar_search(graph, start, goal) -> same dict
A tuple (path, cost, explored, time) is also accepted.
Until those files are implemented, the app shows a "not ready yet" message
for that algorithm; building and costing the player's route still works.
"""

import importlib
import inspect
import math
import time
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from game.graph import currencies, graph, get_conversion_cost, get_neighbors
from game.game_logic import calculate_route_cost, evaluate_player_route, validate_route


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Currency Quest", page_icon="💱", layout="wide")

GOLD = "#E9B949"
GREEN = "#3DD68C"
MUTED = "#8A93A6"
TEXT = "#E8ECF4"


def load_css():
    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


load_css()


# ---------------------------------------------------------------------------
# Algorithms (UCS / A*) — loaded from teammates' modules when available
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "UCS": ("algorithms.ucs", ["uniform_cost_search", "ucs", "search"]),
    "A*": ("algorithms.astar", ["astar_search", "a_star_search", "astar", "a_star", "search"]),
}


def find_algorithm(module_name, function_names):
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return None
    for name in function_names:
        fn = getattr(module, name, None)
        if callable(fn):
            return fn
    return None


def normalize_result(result, elapsed):
    if isinstance(result, dict):
        path = result.get("path") or result.get("route") or []
        cost = result.get("cost", result.get("total_cost"))
        explored = result.get("explored", result.get("explored_nodes", []))
        seconds = result.get("time", result.get("execution_time", elapsed))
    else:
        path, cost, explored, *rest = result
        seconds = rest[0] if rest else elapsed
    explored_list = list(explored) if not isinstance(explored, int) else []
    explored_count = explored if isinstance(explored, int) else len(explored_list)
    return {
        "path": list(path),
        "cost": cost,
        "explored": explored_list,
        "explored_count": explored_count,
        "time_ms": seconds * 1000,
    }


def run_algorithm(label, start, goal):
    """Run a teammate's algorithm. Returns None if its file is not implemented yet."""
    module_name, names = ALGORITHMS[label]
    fn = find_algorithm(module_name, names)
    if fn is None:
        return None
    try:
        began = time.perf_counter()
        takes_graph = len(inspect.signature(fn).parameters) >= 3
        result = fn(graph, start, goal) if takes_graph else fn(start, goal)
        elapsed = time.perf_counter() - began
        return normalize_result(result, elapsed)
    except Exception as error:
        return {"error": f"{type(error).__name__}: {error}"}


def module_file(label):
    return ALGORITHMS[label][0].replace(".", "/") + ".py"


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

def reset_route():
    st.session_state.route = [st.session_state.start]
    st.session_state.submitted = False


if "start" not in st.session_state:
    st.session_state.start = "SAR"
    st.session_state.target = "JPY"
    reset_route()


def on_start_change():
    if st.session_state.target == st.session_state.start:
        st.session_state.target = next(c for c in currencies if c != st.session_state.start)
    reset_route()


# ---------------------------------------------------------------------------
# Helpers for display
# ---------------------------------------------------------------------------

def route_chips(route, highlight_last=True):
    parts = []
    for i, code in enumerate(route):
        cls = "chip chip-current" if highlight_last and i == len(route) - 1 else "chip"
        parts.append(f'<span class="{cls}">{code}</span>')
    return '<div class="route">' + '<span class="arrow">→</span>'.join(parts) + "</div>"


def node_positions():
    positions = {}
    for i, code in enumerate(currencies):
        angle = math.pi / 2 - 2 * math.pi * i / len(currencies)
        positions[code] = (math.cos(angle), math.sin(angle))
    return positions


def graph_figure(player_route=None, optimal_route=None, current=None):
    pos = node_positions()
    fig = go.Figure()

    drawn = set()
    label_x, label_y, label_text = [], [], []
    for source, edges in graph.items():
        for target, weight in edges.items():
            key = tuple(sorted((source, target)))
            if key in drawn:
                continue
            drawn.add(key)
            (x0, y0), (x1, y1) = pos[source], pos[target]
            fig.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1], mode="lines",
                line=dict(color="rgba(138,147,166,0.35)", width=2),
                hoverinfo="skip", showlegend=False,
            ))
            label_x.append((x0 + x1) / 2)
            label_y.append((y0 + y1) / 2)
            label_text.append(str(weight))

    def route_trace(route, color, name, dash):
        if not route or len(route) < 2:
            return
        xs = [pos[c][0] for c in route]
        ys = [pos[c][1] for c in route]
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="lines", name=name,
            line=dict(color=color, width=6 if dash == "solid" else 4, dash=dash),
            hoverinfo="skip",
        ))

    route_trace(optimal_route, GREEN, "Optimal route", "dash")
    route_trace(player_route, GOLD, "Your route", "solid")

    fig.add_trace(go.Scatter(
        x=label_x, y=label_y, mode="text", text=label_text,
        textfont=dict(color=TEXT, size=13), hoverinfo="skip", showlegend=False,
    ))

    node_colors = [GOLD if c == current else "#1E2A44" for c in currencies]
    fig.add_trace(go.Scatter(
        x=[pos[c][0] for c in currencies], y=[pos[c][1] for c in currencies],
        mode="markers+text", text=currencies, textposition="middle center",
        textfont=dict(color=[("#111" if c == current else TEXT) for c in currencies], size=14),
        marker=dict(size=52, color=node_colors, line=dict(color=GOLD, width=2)),
        hovertext=[
            f"{c}<br>" + "<br>".join(f"→ {n}: {w}" for n, w in graph[c].items())
            for c in currencies
        ],
        hoverinfo="text", showlegend=False,
    ))

    fig.update_layout(
        height=430, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, range=[-1.3, 1.3]),
        yaxis=dict(visible=False, range=[-1.3, 1.3], scaleanchor="x"),
        legend=dict(orientation="h", y=-0.02, font=dict(color=TEXT)),
        font=dict(color=TEXT),
    )
    return fig


def comparison_figure(results):
    labels = list(results.keys())
    colors = [GOLD, GREEN]
    fig = make_subplots(rows=1, cols=3, subplot_titles=("Path cost", "Explored nodes", "Execution time (ms)"))
    metrics = ["cost", "explored_count", "time_ms"]
    for col, metric in enumerate(metrics, start=1):
        fig.add_trace(go.Bar(
            x=labels, y=[results[l][metric] for l in labels],
            marker_color=colors, showlegend=False,
            text=[f"{results[l][metric]:.3f}" if metric == "time_ms" else results[l][metric] for l in labels],
            textposition="outside",
        ), row=1, col=col)
    fig.update_layout(
        height=330, margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT),
    )
    fig.update_yaxes(gridcolor="rgba(138,147,166,0.15)", rangemode="tozero")
    return fig


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <div class="hero-badge">💱 Search Algorithms Game</div>
        <h1>Currency Quest</h1>
        <p>Convert your money from one currency to another for the lowest total cost —
        then see if you beat Uniform Cost Search and A*.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.05, 1], gap="large")

# ---------------------------------------------------------------------------
# Left: setup + route builder
# ---------------------------------------------------------------------------

with left:
    st.markdown('<div class="step">1 · Choose your currencies</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.selectbox("Starting currency", currencies, key="start", on_change=on_start_change)
    c2.selectbox(
        "Target currency",
        [c for c in currencies if c != st.session_state.start],
        key="target",
        on_change=reset_route,
    )

    st.markdown('<div class="step">2 · Build your route</div>', unsafe_allow_html=True)

    route = st.session_state.route
    current = route[-1]
    reached = current == st.session_state.target and len(route) > 1
    cost_so_far = calculate_route_cost(route) if len(route) > 1 else 0

    st.markdown(route_chips(route), unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    m1.metric("Current currency", current)
    m2.metric("Cost so far", cost_so_far)
    m3.metric("Conversions", len(route) - 1)

    if not reached:
        st.caption(f"Convert **{current}** to one of its connected currencies:")
        neighbors = get_neighbors(current)
        cols = st.columns(len(neighbors))
        for col, (code, weight) in zip(cols, neighbors.items()):
            if col.button(f"{code}  ·  +{weight}", key=f"move-{code}", width="stretch"):
                st.session_state.route.append(code)
                st.session_state.submitted = False
                st.rerun()
    else:
        st.success(f"You reached {st.session_state.target}! Submit your route to compare it with the AI.")

    b1, b2, b3 = st.columns(3)
    if b1.button("↩ Undo", width="stretch", disabled=len(route) < 2):
        st.session_state.route.pop()
        st.session_state.submitted = False
        st.rerun()
    if b2.button("⟲ Reset", width="stretch", disabled=len(route) < 2):
        reset_route()
        st.rerun()
    if b3.button("Submit route", type="primary", width="stretch", disabled=not reached):
        st.session_state.submitted = True

# ---------------------------------------------------------------------------
# Right: graph map
# ---------------------------------------------------------------------------

results = None
ready = {}
optimal_route = None
if st.session_state.submitted:
    results = {label: run_algorithm(label, st.session_state.start, st.session_state.target) for label in ALGORITHMS}
    ready = {label: r for label, r in results.items() if r and "error" not in r and r["path"]}
    if ready:
        optimal_route = next(iter(ready.values()))["path"]

with right:
    st.markdown('<div class="step">Currency map</div>', unsafe_allow_html=True)
    st.plotly_chart(
        graph_figure(route, optimal_route, current),
        width="stretch",
        config={"displayModeBar": False},
    )
    st.caption("Numbers on the lines are conversion costs. Hover a currency to see its connections.")

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

if results is not None:
    st.markdown('<div class="step">3 · Results</div>', unsafe_allow_html=True)

    for label, r in results.items():
        if r is None:
            st.info(f"{label} is not ready yet (`{module_file(label)}`).")
        elif "error" in r:
            st.error(f"{label} raised an error (`{module_file(label)}`): {r['error']}")

    if not ready:
        st.markdown('<div class="panel-title">Your route</div>', unsafe_allow_html=True)
        st.markdown(route_chips(route, highlight_last=False), unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        p1.metric("Total cost", calculate_route_cost(route))
        p2.metric("Conversions", len(route) - 1)
        st.caption("The comparison with the optimal route will appear once UCS or A* is ready.")
        st.stop()

    evaluation = evaluate_player_route(route, optimal_route)

    if evaluation["optimal"]:
        st.markdown(
            '<div class="verdict verdict-win">🏆 Optimal! Your route costs exactly as little as the AI\'s.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="verdict verdict-miss">Your route costs <b>{evaluation["difference"]}</b> more '
            f"than the optimal route. Try again!</div>",
            unsafe_allow_html=True,
        )

    r1, r2 = st.columns(2)
    with r1:
        st.markdown('<div class="panel-title">Your route</div>', unsafe_allow_html=True)
        st.markdown(route_chips(route, highlight_last=False), unsafe_allow_html=True)
        p1, p2 = st.columns(2)
        p1.metric("Total cost", evaluation["cost"])
        p2.metric("Conversions", len(route) - 1)
    with r2:
        st.markdown('<div class="panel-title">Optimal route (AI)</div>', unsafe_allow_html=True)
        st.markdown(route_chips(optimal_route, highlight_last=False), unsafe_allow_html=True)
        o1, o2 = st.columns(2)
        o1.metric("Total cost", evaluation["optimal_cost"])
        o2.metric("Conversions", len(optimal_route) - 1)

    st.markdown('<div class="panel-title">UCS vs A*</div>', unsafe_allow_html=True)
    table = pd.DataFrame(
        [
            {
                "Algorithm": label,
                "Route": " → ".join(r["path"]),
                "Total cost": r["cost"],
                "Conversions": len(r["path"]) - 1,
                "Explored nodes": r["explored_count"],
                "Exploration order": " → ".join(r["explored"]),
                "Time (ms)": round(r["time_ms"], 4),
            }
            for label, r in ready.items()
        ]
    )
    st.markdown(table.to_html(index=False, classes="results-table", border=0), unsafe_allow_html=True)
    st.plotly_chart(comparison_figure(ready), width="stretch", config={"displayModeBar": False})
