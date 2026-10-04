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
    Renders an authentic 2-Loop Industrial P&ID Mimic Diagram (ISA-5.1 / ISA-18.2):
    1. Loop 1 (Top): Main Hydrocarbon Gas Train with Anti-Surge Recycle Loop (FV-3201).
    2. Loop 2 (Bottom): Auxiliary Closed Lube Oil Circuit (HE-3301 Cooler feeding KO-3201 Bearing).
    Grounded in RCA-2 investigation: Tube leakage in HE-3301 contaminates bearing lubricant,
    raising VI-3201 vibration while main process gas flow (FT-3201, PT-3201) remains stable.
    """
    # Operational condition states
    if current_hour >= 679:
        vib_color = CHANDRA_THEME["grey"]
        vib_status = "TRIP / MACHINE STOPPED"
        lube_color = CHANDRA_THEME["grey"]
    elif current_vibration >= 75.0 or current_hour >= 678:
        vib_color = CHANDRA_THEME["red"]
        vib_status = "CRITICAL (TRIP HAZARD 75 µm)"
        lube_color = CHANDRA_THEME["red"]
    elif current_vibration >= 45.0 or current_hour >= 649:
        vib_color = CHANDRA_THEME["yellow"]
        vib_status = "ALARM (DCS EXCURSION 45 µm)"
        lube_color = CHANDRA_THEME["yellow"]
    elif current_hour >= 633:
        vib_color = CHANDRA_THEME["amber"]
        vib_status = "EARLY WARNING (GDN ANOMALY)"
        lube_color = CHANDRA_THEME["amber"]
    else:
        vib_color = CHANDRA_THEME["green"]
        vib_status = "NORMAL (IN-SPEC)"
        lube_color = CHANDRA_THEME["green"]

    fig = go.Figure()

    # =========================================================================
    # LOOP 1: MAIN HYDROCARBON CRACKING GAS TRAIN (Y = 1.7)
    # =========================================================================
    # Main Gas Header Line
    fig.add_trace(
        go.Scatter(
            x=[0.6, 7.8],
            y=[1.7, 1.7],
            mode="lines",
            line=dict(color="#475569", width=4),
            hoverinfo="none",
            showlegend=False,
        )
    )

    # Main Gas Flow Directional Arrows
    for ax in [1.8, 3.8, 6.0, 7.4]:
        fig.add_annotation(
            x=ax, y=1.7,
            showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=2.5, arrowcolor="#94A3B8",
            ax=-14, ay=0,
        )

    # Anti-Surge Recycle Loop Line (Discharge -> Up -> Left -> Suction Drum)
    fig.add_trace(
        go.Scatter(
            x=[6.8, 6.8, 2.7, 2.7],
            y=[1.7, 2.45, 2.45, 1.7],
            mode="lines",
            line=dict(color="#38BDF8", width=2, dash="dash"),
            hoverinfo="text",
            hovertext="Anti-Surge Recycle Header (Gas Bypass)",
            showlegend=False,
        )
    )
    # Anti-Surge Recycle Arrow
    fig.add_annotation(
        x=4.4, y=2.45,
        showarrow=True, arrowhead=2, arrowsize=1.1, arrowwidth=2, arrowcolor="#38BDF8",
        ax=14, ay=0,
    )
    # Anti-Surge Control Valve (FV-3201)
    fig.add_trace(
        go.Scatter(
            x=[4.8], y=[2.45],
            mode="markers+text",
            marker=dict(size=30, color=CHANDRA_THEME["green"], symbol="bowtie", line=dict(color="#F8FAFC", width=1.5)),
            text=["FV-3201"],
            textposition="top center",
            textfont=dict(color="#38BDF8", size=9, family="Inter, monospace"),
            hovertext="<b>Anti-Surge Control Valve FV-3201</b><br>State: Standby / Normal In-Spec",
            hoverinfo="text",
            showlegend=False,
        )
    )

    # =========================================================================
    # LOOP 2: AUXILIARY CLOSED-LOOP LUBE OIL CIRCUIT (Y = 0.55)
    # =========================================================================
    # Lube Oil Supply Header: Tank -> Pump -> Cooler HE-3301 -> KO-3201 Bearing
    fig.add_trace(
        go.Scatter(
            x=[1.4, 3.0, 4.8, 4.8],
            y=[0.55, 0.55, 0.55, 1.45],
            mode="lines",
            line=dict(color=lube_color, width=3, dash="solid" if lube_color == CHANDRA_THEME["green"] else "dashdot"),
            hoverinfo="text",
            hovertext="Lube Oil Supply Line (ISO VG 46)",
            showlegend=False,
        )
    )
    # Lube Supply Arrow to Bearing
    fig.add_annotation(
        x=4.8, y=1.2,
        showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=2.5, arrowcolor=lube_color,
        ax=0, ay=14,
    )

    # Lube Oil Return Line: Bearing -> Drop -> Tank
    fig.add_trace(
        go.Scatter(
            x=[5.2, 5.2, 1.4, 1.4],
            y=[1.45, 0.2, 0.2, 0.55],
            mode="lines",
            line=dict(color="#64748B", width=2, dash="dot"),
            hoverinfo="text",
            hovertext="Lube Oil Gravity Return Line to Sump Tank",
            showlegend=False,
        )
    )

    # =========================================================================
    # TRANSMITTER & EQUIPMENT NODES
    # =========================================================================
    # 1. Feed Gas (FT-3201)
    fig.add_trace(
        go.Scatter(
            x=[1.0], y=[1.7],
            mode="markers+text",
            marker=dict(size=38, color=CHANDRA_THEME["green"], line=dict(color="#F8FAFC", width=1.5)),
            text=["FT-3201"],
            textposition="middle center",
            textfont=dict(color="#0F172A", size=9, family="Inter, monospace", weight="bold"),
            hovertext="<b>Feed Gas Flow FT-3201</b><br>Rate: 55.4 T/H (Normal Steady)",
            hoverinfo="text",
            showlegend=False,
        )
    )
    fig.add_annotation(
        x=1.0, y=1.35, text="<b>FEED GAS</b><br>55.4 T/H",
        showarrow=False, font=dict(color="#94A3B8", size=9), align="center",
    )

    # 2. Suction Knock-Out Drum (V-3201 / PT-3201)
    fig.add_trace(
        go.Scatter(
            x=[2.7], y=[1.7],
            mode="markers+text",
            marker=dict(size=44, color=CHANDRA_THEME["green"], symbol="square", line=dict(color="#F8FAFC", width=1.5)),
            text=["V-3201"],
            textposition="middle center",
            textfont=dict(color="#0F172A", size=9, family="Inter, monospace", weight="bold"),
            hovertext="<b>Suction KO Drum V-3201</b><br>Pressure PT-3201: 3.2 kg/cm²",
            hoverinfo="text",
            showlegend=False,
        )
    )
    fig.add_annotation(
        x=2.7, y=1.35, text="<b>SUCTION DRUM</b><br>PT-3201: 3.2 kg/cm²",
        showarrow=False, font=dict(color="#94A3B8", size=9), align="center",
    )

    # 3. Cracked Gas Compressor (KO-3201 / VI-3201 / TI-3201)
    fig.add_trace(
        go.Scatter(
            x=[4.8], y=[1.7],
            mode="markers+text",
            marker=dict(size=52, color=vib_color, symbol="hexagon", line=dict(color="#F8FAFC", width=2)),
            text=["KO-3201"],
            textposition="middle center",
            textfont=dict(color="#0F172A", size=10, family="Inter, monospace", weight="bold"),
            hovertext=f"<b>Cracked Gas Compressor KO-3201</b><br>Vibration VI-3201: {current_vibration:.2f} µm<br>Bearing Temp TI-3201: 64.5 °C<br>Status: {vib_status}",
            hoverinfo="text",
            showlegend=False,
        )
    )
    # Bearing Vibration Transmitter Badge above compressor
    fig.add_trace(
        go.Scatter(
            x=[4.8], y=[2.1],
            mode="markers+text",
            marker=dict(size=34, color=vib_color, line=dict(color="#F8FAFC", width=1.5)),
            text=["VI-3201"],
            textposition="middle center",
            textfont=dict(color="#0F172A", size=8, family="Inter, monospace", weight="bold"),
            hovertext=f"<b>Radial Vibration Transmitter VI-3201</b><br>Reading: {current_vibration:.2f} µm<br>Thresholds: Alarm 45 µm | Trip 75 µm",
            hoverinfo="text",
            showlegend=False,
        )
    )
    fig.add_annotation(
        x=4.8, y=1.35, text=f"<b>DE JOURNAL BEARING</b><br><span style='color:{vib_color};'>{current_vibration:.1f} µm</span>",
        showarrow=False, font=dict(color="#F8FAFC", size=9), align="center",
    )

    # 4. Gas Discharge Train (PT-3202)
    fig.add_trace(
        go.Scatter(
            x=[7.0], y=[1.7],
            mode="markers+text",
            marker=dict(size=38, color=CHANDRA_THEME["green"], line=dict(color="#F8FAFC", width=1.5)),
            text=["PT-3202"],
            textposition="middle center",
            textfont=dict(color="#0F172A", size=9, family="Inter, monospace", weight="bold"),
            hovertext="<b>Discharge Pressure PT-3202</b><br>Reading: 18.2 kg/cm² (Normal)",
            hoverinfo="text",
            showlegend=False,
        )
    )
    fig.add_annotation(
        x=7.0, y=1.35, text="<b>DISCHARGE TRAIN</b><br>18.2 kg/cm²",
        showarrow=False, font=dict(color="#94A3B8", size=9), align="center",
    )

    # 5. Lube Oil Sump Tank & Pump (TK-3301 & PM-3301)
    fig.add_trace(
        go.Scatter(
            x=[1.4], y=[0.55],
            mode="markers+text",
            marker=dict(size=34, color="#334155", symbol="square", line=dict(color="#64748B", width=1.5)),
            text=["TK-3301"],
            textposition="middle center",
            textfont=dict(color="#F8FAFC", size=8, family="Inter, monospace"),
            hovertext="<b>Lube Oil Sump Tank TK-3301</b><br>Fluid: Synthetic ISO VG 46",
            hoverinfo="text",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[3.0], y=[0.55],
            mode="markers+text",
            marker=dict(size=34, color="#334155", symbol="circle", line=dict(color="#64748B", width=1.5)),
            text=["PM-3301"],
            textposition="middle center",
            textfont=dict(color="#F8FAFC", size=8, family="Inter, monospace"),
            hovertext="<b>Lube Oil Circulation Pump PM-3301</b><br>State: Running In-Spec",
            hoverinfo="text",
            showlegend=False,
        )
    )

    # 6. Lube Oil Cooler (HE-3301 / TI-3301) - Root Cause Location!
    fig.add_trace(
        go.Scatter(
            x=[4.8], y=[0.55],
            mode="markers+text",
            marker=dict(size=44, color=lube_color, symbol="diamond", line=dict(color="#F8FAFC", width=2)),
            text=["HE-3301"],
            textposition="middle center",
            textfont=dict(color="#0F172A", size=9, family="Inter, monospace", weight="bold"),
            hovertext=f"<b>Lube Oil Cooler HE-3301 (RCA-2 Focus)</b><br>Oil Temp TI-3301: 42.5 °C<br>Cooling Water dP: Anomaly Indication<br>Status: {'SUSPECT TUBE LEAK (WATER INGRESS)' if current_hour >= 633 else 'NORMAL'}",
            hoverinfo="text",
            showlegend=False,
        )
    )
    fig.add_annotation(
        x=4.8, y=0.15,
        text=f"<b>LUBE OIL COOLER (HE-3301)</b><br><span style='color:{lube_color};'>TI-3301: 42.5 °C ({'TUBE LEAK' if current_hour >= 633 else 'IN-SPEC'})</span>",
        showarrow=False, font=dict(color="#F8FAFC", size=9), align="center",
    )

    # P&ID Diagram Canvas Layout
    fig.update_layout(
        title=dict(
            text=f"Plant ZCU 2-Loop Process P&ID (Gas Train + Lube Auxiliary System) — Hour {current_hour}",
            font=dict(size=12, color=CHANDRA_THEME["text_secondary"]),
        ),
        paper_bgcolor=CHANDRA_THEME["card_bg"],
        plot_bgcolor=CHANDRA_THEME["card_bg"],
        height=320,
        margin=dict(l=20, r=20, t=35, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.2, 8.2]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.05, 2.7]),
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
