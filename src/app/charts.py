"""
Plotly Interactive Visualization Engine for Chandra Asri SPOG Dashboard.
Renders industrial-grade Gauges, Multi-Sensor Telemetry Trends, Dynamic P&ID Graphs,
and P-F Curve Decision Escalation visual components.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


CHANDRA_THEME = {
    "bg_dark": "#0B1120",
    "card_bg": "#1E293B",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "grid_color": "#334155",
    "green": "#10B981",
    "yellow": "#F59E0B",
    "red": "#EF4444",
    "cyan": "#38BDF8",
    "purple": "#A855F7",
    "grey": "#64748B",
}


def create_health_index_gauge(
    hi_val: float,
    status_color: str = "GREEN",
    operational_state: int = 2,
) -> go.Figure:
    """
    Renders an industrial radial Health Index Gauge (0 - 100%).
    Threshold bands: Red < 65%, Yellow 65-84.9%, Green >= 85%.
    """
    color_map = {
        "GREEN": CHANDRA_THEME["green"],
        "AMBER": CHANDRA_THEME["yellow"],
        "YELLOW": CHANDRA_THEME["yellow"],
        "RED": CHANDRA_THEME["red"],
        "GREY": CHANDRA_THEME["grey"],
    }
    bar_color = color_map.get(status_color.upper(), CHANDRA_THEME["green"])

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(hi_val),
            number={"suffix": "%", "font": {"size": 38, "color": CHANDRA_THEME["text_primary"], "family": "Inter, sans-serif"}},
            title={"text": "Asset Health Index (ISO 10816-3)", "font": {"size": 15, "color": CHANDRA_THEME["text_secondary"]}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": CHANDRA_THEME["grid_color"], "tickfont": {"color": CHANDRA_THEME["text_secondary"]}},
                "bar": {"color": bar_color, "thickness": 0.3},
                "bgcolor": CHANDRA_THEME["bg_dark"],
                "borderwidth": 1,
                "bordercolor": CHANDRA_THEME["grid_color"],
                "steps": [
                    {"range": [0, 65], "color": "rgba(239, 68, 68, 0.25)"},
                    {"range": [65, 85], "color": "rgba(245, 158, 11, 0.25)"},
                    {"range": [85, 100], "color": "rgba(16, 185, 129, 0.25)"},
                ],
                "threshold": {
                    "line": {"color": CHANDRA_THEME["text_primary"], "width": 3},
                    "thickness": 0.8,
                    "value": float(hi_val),
                },
            },
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=25, r=25, t=40, b=20),
        height=220,
    )
    return fig


def create_telemetry_trend_chart(
    df: pd.DataFrame,
    current_hour: int = 633,
) -> go.Figure:
    """
    Multi-sensor 720-hour timeline chart featuring:
    Row 1: Vibration Radial Poros (KO3201_VIB) with Normal, Alarm, and Trip Setpoint (75 um) lines.
    Row 2: GDN Anomaly Score with threshold tau = 3.11.
    Current Hour cursor marker line across both rows.
    """
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=(
            "Radial Vibration (KO3201_VIB) vs Operational Thresholds",
            "Graph Deviation Network (GDN) Multimodal Anomaly Score",
        ),
        row_heights=[0.65, 0.35],
    )

    hours = df["hour"]

    # --- Row 1: Vibration Telemetry ---
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=df["KO3201_VIB"],
            mode="lines",
            name="Vibration (µm)",
            line=dict(color=CHANDRA_THEME["cyan"], width=2),
            hovertemplate="Hour %{x}: %{y:.2f} µm<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # Threshold horizontal reference lines
    # Normal Baseline (30 um)
    fig.add_hline(
        y=30.0,
        line=dict(color=CHANDRA_THEME["green"], width=1.5, dash="dash"),
        annotation_text="Normal Baseline (30 µm)",
        annotation_position="bottom left",
        annotation_font=dict(color=CHANDRA_THEME["green"], size=11),
        row=1,
        col=1,
    )
    # DCS Alarm (45 um)
    fig.add_hline(
        y=45.0,
        line=dict(color=CHANDRA_THEME["yellow"], width=1.5, dash="dash"),
        annotation_text="DCS Alarm Threshold (45 µm)",
        annotation_position="top left",
        annotation_font=dict(color=CHANDRA_THEME["yellow"], size=11),
        row=1,
        col=1,
    )
    # Trip Setpoint Line (75 um) - Solution C6
    fig.add_hline(
        y=75.0,
        line=dict(color=CHANDRA_THEME["red"], width=2, dash="solid"),
        annotation_text="Safety Interlock Trip Setpoint (75 µm)",
        annotation_position="top left",
        annotation_font=dict(color=CHANDRA_THEME["red"], size=11),
        row=1,
        col=1,
    )

    # --- Row 2: GDN Anomaly Score ---
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=df["gdn_anomaly_score"],
            mode="lines",
            name="GDN Score",
            line=dict(color=CHANDRA_THEME["purple"], width=2),
            hovertemplate="Hour %{x}: Score %{y:.2f}<extra></extra>",
        ),
        row=2,
        col=1,
    )
    # Anomaly Threshold tau = 3.11
    fig.add_hline(
        y=3.11,
        line=dict(color=CHANDRA_THEME["red"], width=1.5, dash="dash"),
        annotation_text="Anomaly Threshold (τ = 3.11)",
        annotation_position="top left",
        annotation_font=dict(color=CHANDRA_THEME["red"], size=10),
        row=2,
        col=1,
    )

    # Current Hour vertical line cursor
    for r in [1, 2]:
        fig.add_vline(
            x=current_hour,
            line=dict(color=CHANDRA_THEME["text_primary"], width=2, dash="dot"),
            annotation_text=f"Selected: Hr {current_hour}" if r == 1 else "",
            annotation_position="top right",
            annotation_font=dict(color=CHANDRA_THEME["text_primary"], size=11),
            row=r,
            col=1,
        )

    fig.update_layout(
        paper_bgcolor=CHANDRA_THEME["bg_dark"],
        plot_bgcolor=CHANDRA_THEME["card_bg"],
        font=dict(color=CHANDRA_THEME["text_primary"], family="Inter, sans-serif"),
        height=480,
        margin=dict(l=50, r=30, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor=CHANDRA_THEME["grid_color"], title_text="Operational Timeline (Hours)", row=2, col=1)
    fig.update_xaxes(gridcolor=CHANDRA_THEME["grid_color"], row=1, col=1)
    fig.update_yaxes(gridcolor=CHANDRA_THEME["grid_color"], title_text="Vibration (µm)", row=1, col=1)
    fig.update_yaxes(gridcolor=CHANDRA_THEME["grid_color"], title_text="Score", row=2, col=1)

    return fig


def create_pid_deviation_graph(
    top_contributors: List[Any],
    current_hour: int = 633,
) -> go.Figure:
    """
    Renders the topological P&ID sensor graph (6 nodes) with dynamic deviation highlighting (Solution H4).
    Nodes exceeding local anomaly scores are highlighted in Red/Amber, while normal process nodes remain Green.
    """
    # Fixed 2D node coordinates
    node_coords = {
        "PLANT_RATE": (0.0, 1.0),
        "KO3201_FEED": (1.2, 1.0),
        "KO3201_DISP": (2.4, 1.6),
        "KO3201_AMP": (2.4, 0.4),
        "KO3201_TEMP": (3.6, 1.0),
        "KO3201_VIB": (4.8, 1.0),
    }

    edges = [
        ("PLANT_RATE", "KO3201_FEED"),
        ("KO3201_FEED", "KO3201_DISP"),
        ("KO3201_FEED", "KO3201_AMP"),
        ("KO3201_DISP", "KO3201_TEMP"),
        ("KO3201_AMP", "KO3201_TEMP"),
        ("KO3201_TEMP", "KO3201_VIB"),
    ]

    # Parse deviating contributors dict
    contrib_dict = {}
    if isinstance(top_contributors, list):
        for item in top_contributors:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                contrib_dict[str(item[0])] = float(item[1])

    fig = go.Figure()

    # Draw edge lines
    for u, v in edges:
        x0, y0 = node_coords[u]
        x1, y1 = node_coords[v]
        fig.add_trace(
            go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode="lines",
                line=dict(color=CHANDRA_THEME["grid_color"], width=2),
                hoverinfo="none",
                showlegend=False,
            )
        )

    # Draw nodes
    node_x = []
    node_y = []
    node_colors = []
    node_texts = []
    hover_texts = []

    for name, (x, y) in node_coords.items():
        node_x.append(x)
        node_y.append(y)
        dev_score = contrib_dict.get(name, 0.0)

        # Highlight in red only if it's an anomaly contributor with score > 1.5 (Solution H4)
        if dev_score > 3.0:
            node_colors.append(CHANDRA_THEME["red"])
            status_desc = f"DEVIATING (Score: {dev_score:.2f})"
        elif dev_score > 1.0:
            node_colors.append(CHANDRA_THEME["yellow"])
            status_desc = f"ELEVATED (Score: {dev_score:.2f})"
        else:
            node_colors.append(CHANDRA_THEME["green"])
            status_desc = "NORMAL STEADY (Correlation Stable)"

        node_texts.append(f"<b>{name}</b>")
        hover_texts.append(f"<b>Node: {name}</b><br>Status: {status_desc}")

    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            marker=dict(
                size=44,
                color=node_colors,
                line=dict(color=CHANDRA_THEME["text_primary"], width=2),
            ),
            text=node_texts,
            textposition="top center",
            textfont=dict(color=CHANDRA_THEME["text_primary"], size=12, family="Inter, sans-serif"),
            hovertext=hover_texts,
            hoverinfo="text",
            showlegend=False,
        )
    )

    fig.update_layout(
        title=f"P&ID Graph Sensor Correlation & Anomaly Attribution (Hour {current_hour})",
        paper_bgcolor=CHANDRA_THEME["bg_dark"],
        plot_bgcolor=CHANDRA_THEME["card_bg"],
        font=dict(color=CHANDRA_THEME["text_primary"], family="Inter, sans-serif"),
        height=280,
        margin=dict(l=30, r=30, t=50, b=30),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 5.5]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.2, 2.2]),
    )
    return fig


def create_pf_escalation_chart(
    current_action_hour: int = 633,
    plant_rate: float = 55.0,
    price_per_ton: float = 900.0,
) -> go.Figure:
    """
    Visualizes the industrial P-F Curve Decision Escalation model (Solution C1, H3).
    Displays the turnaround downtime escalation curve (8h -> 32h) and net savings curve.
    """
    hours = np.arange(633, 680)  # [633 .. 679]
    downtimes = []
    savings = []

    for t in hours:
        fraction = (t - 633.0) / 46.0
        dt = 8.0 + (fraction ** 2) * 24.0
        loss = dt * plant_rate * (price_per_ton / 1000.0)
        uncontrolled_loss = 32.0 * plant_rate * (price_per_ton / 1000.0)
        net_save = max(0.0, uncontrolled_loss - loss)
        downtimes.append(round(dt, 1))
        savings.append(round(net_save, 1))

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Downtime Curve (Left Axis)
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=downtimes,
            mode="lines",
            name="Turnaround Downtime (Hours)",
            line=dict(color=CHANDRA_THEME["yellow"], width=3),
            hovertemplate="Action Hr %{x}: %{y:.1f} hrs downtime<extra></extra>",
        ),
        secondary_y=False,
    )

    # Net Savings Curve (Right Axis)
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=savings,
            mode="lines",
            name="Net Cost Savings ($k USD)",
            line=dict(color=CHANDRA_THEME["green"], width=3, dash="dot"),
            hovertemplate="Action Hr %{x}: $%{y:.1f}k saved<extra></extra>",
        ),
        secondary_y=True,
    )

    # Milestone points
    # Point P (Hour 633)
    fig.add_trace(
        go.Scatter(
            x=[633],
            y=[8.0],
            mode="markers+text",
            name="Point P (Early Warning)",
            marker=dict(size=14, color=CHANDRA_THEME["green"], symbol="circle"),
            text=["Point P (Hr 633): 8h DT / $1.188M Saved"],
            textposition="top right",
            textfont=dict(color=CHANDRA_THEME["green"], size=11),
            showlegend=False,
        ),
        secondary_y=False,
    )
    # Point F (Hour 679)
    fig.add_trace(
        go.Scatter(
            x=[679],
            y=[32.0],
            mode="markers+text",
            name="Point F (Actual Trip)",
            marker=dict(size=14, color=CHANDRA_THEME["red"], symbol="x"),
            text=["Point F (Hr 679): 32h DT / $0 Saved"],
            textposition="bottom left",
            textfont=dict(color=CHANDRA_THEME["red"], size=11),
            showlegend=False,
        ),
        secondary_y=False,
    )

    # Selected Hour Vertical Marker
    clamped_cur = max(633, min(679, current_action_hour))
    fraction_cur = (clamped_cur - 633.0) / 46.0
    dt_cur = 8.0 + (fraction_cur ** 2) * 24.0
    save_cur = max(0.0, 1584.0 - (dt_cur * 55.0 * 0.9))

    fig.add_vline(
        x=clamped_cur,
        line=dict(color=CHANDRA_THEME["text_primary"], width=2, dash="dash"),
        annotation_text=f"Selected: Hr {clamped_cur} (${save_cur:.1f}k Saved)",
        annotation_position="top left",
        annotation_font=dict(color=CHANDRA_THEME["text_primary"], size=12),
    )

    fig.update_layout(
        title="Industrial P-F Curve Decision Escalation: Cost of Delayed Action",
        paper_bgcolor=CHANDRA_THEME["bg_dark"],
        plot_bgcolor=CHANDRA_THEME["card_bg"],
        font=dict(color=CHANDRA_THEME["text_primary"], family="Inter, sans-serif"),
        height=320,
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor=CHANDRA_THEME["grid_color"], title_text="Response Hour (from Detection to Trip)")
    fig.update_yaxes(gridcolor=CHANDRA_THEME["grid_color"], title_text="Downtime (Hours)", secondary_y=False)
    fig.update_yaxes(gridcolor="rgba(0,0,0,0)", title_text="Savings ($k USD)", secondary_y=True)

    return fig
