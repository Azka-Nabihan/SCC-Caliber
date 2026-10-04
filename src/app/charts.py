"""
Industrial-Grade Visualization Engine for Chandra Asri Plant ZCU Condition Monitoring System.
Complies with ISA-18.2 Alarm Standards, ISA-5.1 Instrumentation Tagging, and High-Density DCS Ergonomics.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Industrial DCS Slate Palette (Flat, High Contrast, Zero Gimmick Glow)
CHANDRA_THEME = {
    "bg_dark": "#0F172A",        # Slate 900 (DCS Background)
    "card_bg": "#1E293B",        # Slate 800 (Panel Background)
    "card_border": "#334155",    # Slate 700 (Crisp Border)
    "text_primary": "#F8FAFC",   # Crisp White
    "text_secondary": "#94A3B8", # Muted Engineering Slate
    "text_muted": "#64748B",     # Dim Labels
    "green": "#10B981",          # ISA Normal / In-Spec
    "amber": "#F59E0B",          # ISA Early Warning (AI Deviation)
    "yellow": "#EAB308",         # ISA Alarm (DCS Threshold)
    "red": "#EF4444",            # ISA Critical / Emergency Trip
    "cyan": "#38BDF8",           # Process Variable / Telemetry
    "purple": "#818CF8",         # Analytical / Algorithm Score
    "grey": "#64748B",           # Offline / Post-Trip
}


def create_health_index_gauge(
    hi_val: float,
    status_color: str = "GREEN",
    operational_state: int = 2,
) -> go.Figure:
    """
    Renders an industrial radial Health Index Gauge (0 - 100%) under ISO 10816-3.
    Threshold bands: Trip/Severe < 65%, Warning 65-84.9%, Normal >= 85%.
    """
    color_map = {
        "GREEN": CHANDRA_THEME["green"],
        "AMBER": CHANDRA_THEME["amber"],
        "YELLOW": CHANDRA_THEME["yellow"],
        "RED": CHANDRA_THEME["red"],
        "GREY": CHANDRA_THEME["grey"],
    }
    bar_color = color_map.get(status_color.upper(), CHANDRA_THEME["green"])

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(hi_val),
            number={
                "suffix": "%",
                "font": {"size": 34, "color": CHANDRA_THEME["text_primary"], "family": "Inter, sans-serif"},
            },
            title={
                "text": "Health Index (ISO 10816-3)",
                "font": {"size": 13, "color": CHANDRA_THEME["text_secondary"]},
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickwidth": 1,
                    "tickcolor": CHANDRA_THEME["card_border"],
                    "tickfont": {"color": CHANDRA_THEME["text_muted"], "size": 10},
                },
                "bar": {"color": bar_color, "thickness": 0.28},
                "bgcolor": CHANDRA_THEME["bg_dark"],
                "borderwidth": 1,
                "bordercolor": CHANDRA_THEME["card_border"],
                "steps": [
                    {"range": [0, 65], "color": "rgba(239, 68, 68, 0.20)"},
                    {"range": [65, 85], "color": "rgba(245, 158, 11, 0.20)"},
                    {"range": [85, 100], "color": "rgba(16, 185, 129, 0.20)"},
                ],
                "threshold": {
                    "line": {"color": CHANDRA_THEME["text_primary"], "width": 2},
                    "thickness": 0.75,
                    "value": float(hi_val),
                },
            },
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=35, b=15),
        height=190,
    )
    return fig


def create_compact_vibration_trend(
    df: pd.DataFrame,
    current_hour: int = 633,
) -> go.Figure:
    """
    Compact single-panel vibration trend for Tab 1 operational console.
    Shows the 16-Hour Lead Time gap directly against the 45 um DCS alarm.
    """
    hours = df["hour"]
    vibs = df["KO3201_VIB"]

    fig = go.Figure()

    # Raw telemetry curve
    fig.add_trace(
        go.Scatter(
            x=hours,
            y=vibs,
            mode="lines",
            name="Radial Vibration",
            line=dict(color=CHANDRA_THEME["cyan"], width=2),
            hovertemplate="Hour %{x}: %{y:.2f} µm<extra></extra>",
        )
    )

    # Reference lines
    fig.add_hline(
        y=45.0,
        line=dict(color=CHANDRA_THEME["yellow"], width=1.5, dash="dash"),
        annotation_text="DCS Alarm (45 µm)",
        annotation_position="top left",
        annotation_font=dict(color=CHANDRA_THEME["yellow"], size=10),
    )
    fig.add_hline(
        y=75.0,
        line=dict(color=CHANDRA_THEME["red"], width=1.5, dash="solid"),
        annotation_text="Trip Setpoint (75 µm)",
        annotation_position="top left",
        annotation_font=dict(color=CHANDRA_THEME["red"], size=10),
    )

    # Cursor line
    fig.add_vline(
        x=current_hour,
        line=dict(color=CHANDRA_THEME["text_primary"], width=1.5, dash="dot"),
        annotation_text=f"Hr {current_hour}",
        annotation_position="top right",
        annotation_font=dict(color=CHANDRA_THEME["text_primary"], size=10),
    )

    fig.update_layout(
        paper_bgcolor=CHANDRA_THEME["card_bg"],
        plot_bgcolor=CHANDRA_THEME["card_bg"],
        font=dict(color=CHANDRA_THEME["text_primary"], family="Inter, sans-serif"),
        height=210,
        margin=dict(l=45, r=20, t=25, b=30),
        showlegend=False,
        hovermode="x unified",
    )
    fig.update_xaxes(
        gridcolor=CHANDRA_THEME["card_border"],
        title_text="Timeline (Hours)",
        title_font=dict(size=10, color=CHANDRA_THEME["text_secondary"]),
        tickfont=dict(size=9, color=CHANDRA_THEME["text_secondary"]),
    )
    fig.update_yaxes(
        gridcolor=CHANDRA_THEME["card_border"],
        title_text="Vibration (µm)",
        title_font=dict(size=10, color=CHANDRA_THEME["text_secondary"]),
        tickfont=dict(size=9, color=CHANDRA_THEME["text_secondary"]),
        range=[20, 80],
    )
    return fig


def create_telemetry_trend_chart(
    df: pd.DataFrame,
    current_hour: int = 633,
) -> go.Figure:
    """
    Detailed two-tier telemetry trend chart for Tab 2:
    Row 1: Vibration Radial Poros (KO3201_VIB) vs Operational Thresholds (30, 45, 75 um).
    Row 2: Graph Deviation Network (GDN) Multimodal Anomaly Score vs tau=3.11 threshold.
    """
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=(
            "Radial Vibration (KO3201_VIB) vs Operational Limits",
            "Multimodal Graph Deviation Network (GDN) Anomaly Score",
        ),
        row_heights=[0.65, 0.35],
    )

    hours = df["hour"]

    # Row 1: Vibration
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

    fig.add_hline(
        y=30.0,
        line=dict(color=CHANDRA_THEME["green"], width=1.2, dash="dash"),
        annotation_text="Normal Baseline (30 µm)",
        annotation_position="bottom left",
        annotation_font=dict(color=CHANDRA_THEME["green"], size=10),
        row=1,
        col=1,
    )
    fig.add_hline(
        y=45.0,
        line=dict(color=CHANDRA_THEME["yellow"], width=1.5, dash="dash"),
        annotation_text="DCS Alarm Threshold (45 µm)",
        annotation_position="top left",
        annotation_font=dict(color=CHANDRA_THEME["yellow"], size=10),
        row=1,
        col=1,
    )
    fig.add_hline(
        y=75.0,
        line=dict(color=CHANDRA_THEME["red"], width=1.8, dash="solid"),
        annotation_text="Safety Interlock Trip Setpoint (75 µm)",
        annotation_position="top left",
        annotation_font=dict(color=CHANDRA_THEME["red"], size=10),
        row=1,
        col=1,
    )

    # Row 2: GDN Score
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
    fig.add_hline(
        y=3.11,
        line=dict(color=CHANDRA_THEME["red"], width=1.5, dash="dash"),
        annotation_text="Anomaly Threshold (τ = 3.11)",
        annotation_position="top left",
        annotation_font=dict(color=CHANDRA_THEME["red"], size=10),
        row=2,
        col=1,
    )

    # Vertical cursor across both subplots
    for r in [1, 2]:
        fig.add_vline(
            x=current_hour,
            line=dict(color=CHANDRA_THEME["text_primary"], width=1.8, dash="dot"),
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
        height=460,
        margin=dict(l=50, r=25, t=45, b=35),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor=CHANDRA_THEME["card_border"], title_text="Timeline (Hours)", row=2, col=1)
    fig.update_xaxes(gridcolor=CHANDRA_THEME["card_border"], row=1, col=1)
    fig.update_yaxes(gridcolor=CHANDRA_THEME["card_border"], title_text="Vibration (µm)", row=1, col=1)
    fig.update_yaxes(gridcolor=CHANDRA_THEME["card_border"], title_text="Score", row=2, col=1)

    return fig


def create_process_mimic_chart(
    top_contributors: List[Any] = None,
    current_hour: int = 633,
    current_vibration: float = 31.24,
) -> go.Figure:
    """
    Renders an authentic horizontal Process Mimic Flow Strip (ISA-5.1 & ISA-18.2).
    Shows chemical process units with standard instrumentation transmitters:
    [Feed Gas: FT-3201] -> [Suction Drum: PT-3201] -> [Compressor KO-3201: VI-3201, TI-3201]
    -> [Lube Cooler HE-3301: TI-3301] -> [Discharge Train: PT-3202]
    """
    # Determine KO-3201 status color based on current condition
    if current_hour >= 679:
        vib_color = CHANDRA_THEME["grey"]
        vib_status = "TRIP / STOPPED"
        vib_tag_bg = CHANDRA_THEME["grey"]
    elif current_vibration >= 75.0 or current_hour >= 678:
        vib_color = CHANDRA_THEME["red"]
        vib_status = "CRITICAL (TRIP HAZARD)"
        vib_tag_bg = CHANDRA_THEME["red"]
    elif current_vibration >= 45.0 or current_hour >= 649:
        vib_color = CHANDRA_THEME["yellow"]
        vib_status = "ALARM (DCS EXCURSION)"
        vib_tag_bg = CHANDRA_THEME["yellow"]
    elif current_hour >= 633:
        vib_color = CHANDRA_THEME["amber"]
        vib_status = "EARLY WARNING (GDN DEV)"
        vib_tag_bg = CHANDRA_THEME["amber"]
    else:
        vib_color = CHANDRA_THEME["green"]
        vib_status = "NORMAL (IN-SPEC)"
        vib_tag_bg = CHANDRA_THEME["green"]

    # 5 Equipment Stage Definitions along X axis
    stages = [
        {
            "x": 0.8,
            "unit": "FEED GAS SUPPLY",
            "tag": "FT-3201",
            "val": "55.4 T/H",
            "param": "Cracked Gas Flow",
            "color": CHANDRA_THEME["green"],
            "status": "NORMAL",
        },
        {
            "x": 2.4,
            "unit": "SUCTION DRUM (V-3201)",
            "tag": "PT-3201",
            "val": "3.2 kg/cm²",
            "param": "Suction Pressure",
            "color": CHANDRA_THEME["green"],
            "status": "NORMAL",
        },
        {
            "x": 4.2,
            "unit": "COMPRESSOR (KO-3201)",
            "tag": "VI-3201",
            "val": f"{current_vibration:.1f} µm",
            "param": "Radial Vibration",
            "color": vib_color,
            "status": vib_status,
        },
        {
            "x": 6.0,
            "unit": "LUBE COOLER (HE-3301)",
            "tag": "TI-3301",
            "val": "42.5 °C",
            "param": "Lube Oil Outlet Temp",
            "color": CHANDRA_THEME["green"],
            "status": "NORMAL",
        },
        {
            "x": 7.6,
            "unit": "DISCHARGE TRAIN",
            "tag": "PT-3202",
            "val": "18.2 kg/cm²",
            "param": "Discharge Pressure",
            "color": CHANDRA_THEME["green"],
            "status": "NORMAL",
        },
    ]

    fig = go.Figure()

    # Draw main process piping header line
    fig.add_trace(
        go.Scatter(
            x=[0.4, 8.0],
            y=[1.0, 1.0],
            mode="lines",
            line=dict(color="#475569", width=4),
            hoverinfo="none",
            showlegend=False,
        )
    )

    # Directional Flow Arrows on Piping
    for arrow_x in [1.6, 3.3, 5.1, 6.8]:
        fig.add_annotation(
            x=arrow_x,
            y=1.0,
            showarrow=True,
            arrowhead=2,
            arrowsize=1.2,
            arrowwidth=2.5,
            arrowcolor="#94A3B8",
            ax=-15,
            ay=0,
        )

    # Draw Stage Blocks and Transmitter Badges
    for s in stages:
        # Transmitter circle marker above process line
        fig.add_trace(
            go.Scatter(
                x=[s["x"]],
                y=[1.45],
                mode="markers+text",
                marker=dict(
                    size=42,
                    color=s["color"],
                    line=dict(color=CHANDRA_THEME["text_primary"], width=1.5),
                ),
                text=[s["tag"]],
                textposition="middle center",
                textfont=dict(color="#0F172A", size=10, family="Inter, monospace", weight="bold"),
                hovertext=f"<b>ISA Tag: {s['tag']}</b><br>Unit: {s['unit']}<br>Parameter: {s['param']}<br>Reading: {s['val']}<br>Status: {s['status']}",
                hoverinfo="text",
                showlegend=False,
            )
        )

        # Transmitter impulse line to piping
        fig.add_trace(
            go.Scatter(
                x=[s["x"], s["x"]],
                y=[1.0, 1.25],
                mode="lines",
                line=dict(color=s["color"], width=1.5, dash="dot"),
                hoverinfo="none",
                showlegend=False,
            )
        )

        # Equipment Unit Text Box below process line
        fig.add_annotation(
            x=s["x"],
            y=0.55,
            text=f"<b>{s['unit']}</b><br><span style='color:{s['color']};font-size:11px;'>{s['val']}</span>",
            showarrow=False,
            font=dict(color=CHANDRA_THEME["text_primary"], size=10, family="Inter, sans-serif"),
            align="center",
            bgcolor=CHANDRA_THEME["card_bg"],
            bordercolor=s["color"],
            borderwidth=1,
            borderpad=5,
        )

    fig.update_layout(
        title=dict(
            text=f"Plant ZCU Process Flow Mimic (ISA-5.1) — Operating Snapshot Hour {current_hour}",
            font=dict(size=13, color=CHANDRA_THEME["text_secondary"]),
        ),
        paper_bgcolor=CHANDRA_THEME["card_bg"],
        plot_bgcolor=CHANDRA_THEME["card_bg"],
        height=220,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.1, 8.3]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.2, 1.8]),
    )

    return fig


def create_pid_deviation_graph(
    top_contributors: List[Any] = None,
    current_hour: int = 633,
) -> go.Figure:
    """
    Backwards compatibility alias redirecting to create_process_mimic_chart().
    """
    return create_process_mimic_chart(
        top_contributors=top_contributors,
        current_hour=current_hour,
        current_vibration=31.24 if current_hour == 633 else 28.5,
    )


def create_pf_escalation_chart(
    current_action_hour: int = 633,
    plant_rate: float = 55.0,
    price_per_ton: float = 900.0,
) -> go.Figure:
    """
    Visualizes the industrial P-F Curve Decision Escalation model (ISO 14224 / API 581).
    Evaluates quadratic downtime degradation between Point P (Hr 633) and Point F (Hr 679).
    """
    delta_t = 46.0  # Hours between 633 and 679
    cost_per_hr = plant_rate * price_per_ton

    hours_range = np.linspace(633, 679, 47)
    downtimes = []
    savings = []

    for h in hours_range:
        elapsed = h - 633
        dt = 8.0 + 24.0 * ((elapsed / delta_t) ** 2)
        downtimes.append(dt)
        saved = max(0.0, (32.0 - dt) * cost_per_hr / 1000.0)
        savings.append(saved)

    # Current selected point calculation
    cur_elapsed = max(0, min(delta_t, current_action_hour - 633))
    cur_dt = 8.0 + 24.0 * ((cur_elapsed / delta_t) ** 2)
    cur_saved = max(0.0, (32.0 - cur_dt) * cost_per_hr / 1000.0)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Downtime Escalation Curve
    fig.add_trace(
        go.Scatter(
            x=hours_range,
            y=downtimes,
            name="Turnaround Downtime (Hours)",
            line=dict(color=CHANDRA_THEME["amber"], width=2.5),
            hovertemplate="Action Hr %{x:.0f}: Downtime %{y:.1f} hrs<extra></extra>",
        ),
        secondary_y=False,
    )

    # Net Cost Savings Curve
    fig.add_trace(
        go.Scatter(
            x=hours_range,
            y=savings,
            name="Net Cost Savings ($k USD)",
            line=dict(color=CHANDRA_THEME["green"], width=2, dash="dot"),
            hovertemplate="Action Hr %{x:.0f}: Savings $%{y:,.1f}k<extra></extra>",
        ),
        secondary_y=True,
    )

    # Current Action Cursor
    fig.add_vline(
        x=current_action_hour,
        line=dict(color=CHANDRA_THEME["text_primary"], width=1.5, dash="dash"),
        annotation_text=f"Selected: Hr {current_action_hour} (${cur_saved:,.0f}k Saved)",
        annotation_position="top left",
        annotation_font=dict(color=CHANDRA_THEME["text_primary"], size=10),
    )

    # Critical Milestone Marker Points
    # Point P (Hour 633)
    fig.add_trace(
        go.Scatter(
            x=[633],
            y=[8.0],
            mode="markers+text",
            marker=dict(color=CHANDRA_THEME["green"], size=10, symbol="circle"),
            text=["Point P (Hr 633: 8h Turnaround)"],
            textposition="top right",
            textfont=dict(color=CHANDRA_THEME["green"], size=10),
            showlegend=False,
            hoverinfo="skip",
        ),
        secondary_y=False,
    )

    # Point F (Hour 679)
    fig.add_trace(
        go.Scatter(
            x=[679],
            y=[32.0],
            mode="markers+text",
            marker=dict(color=CHANDRA_THEME["red"], size=10, symbol="x"),
            text=["Point F (Hr 679: 32h Unplanned Trip)"],
            textposition="top left",
            textfont=dict(color=CHANDRA_THEME["red"], size=10),
            showlegend=False,
            hoverinfo="skip",
        ),
        secondary_y=False,
    )

    fig.update_layout(
        title=dict(
            text="P-F Curve Economic Escalation: Cost of Delayed Operational Intervention",
            font=dict(size=12, color=CHANDRA_THEME["text_secondary"]),
        ),
        paper_bgcolor=CHANDRA_THEME["card_bg"],
        plot_bgcolor=CHANDRA_THEME["card_bg"],
        font=dict(color=CHANDRA_THEME["text_primary"], family="Inter, sans-serif"),
        height=320,
        margin=dict(l=45, r=45, t=45, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
    )
    fig.update_xaxes(
        gridcolor=CHANDRA_THEME["card_border"],
        title_text="Response Hour (from Detection to Trip)",
        title_font=dict(size=10, color=CHANDRA_THEME["text_secondary"]),
    )
    fig.update_yaxes(
        gridcolor=CHANDRA_THEME["card_border"],
        title_text="Downtime (Hours)",
        title_font=dict(size=10, color=CHANDRA_THEME["amber"]),
        secondary_y=False,
    )
    fig.update_yaxes(
        gridcolor=CHANDRA_THEME["card_border"],
        title_text="Savings ($k USD)",
        title_font=dict(size=10, color=CHANDRA_THEME["green"]),
        secondary_y=True,
    )

    return fig
