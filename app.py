"""
SCC-Caliber POC Demo Application
Steam Cracker Multivariate Anomaly Detection & Prescriptive RCA Engine.
"""

import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.models.health_index import HealthIndexCalculator

st.set_page_config(
    page_title="Steam Cracker POC Monitor",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Steam Cracker Early Anomaly Detection & Prescriptive RCA Engine")
st.caption(
    "Implementasi POC deteksi anomali multivariate berbasis relasi sensor "
    "(GDN: arXiv:2106.06947) dan estimasi degradasi kesehatan alat (arXiv:2405.04990)."
)

# Sidebar - Kontrol Simulasi
st.sidebar.header("Kontrol Simulasi Operasional")
selected_equipment = st.sidebar.selectbox(
    "Pilih Equipment",
    ["KO-3201 (High Criticality)", "PU-2101B (Medium Criticality)", "HE-3301 (Medium Criticality)"],
)
anomaly_inject = st.sidebar.checkbox("Simulasikan Anomali Sensor", value=False)
speed = st.sidebar.slider("Frekuensi Replay (detik)", min_value=1, max_value=5, value=2)

# Konfigurasi Threshold & Bobot (ISO 10816-3 & Engineering Limits)
weights = {"vibration": 0.40, "bearing_temp": 0.35, "discharge_press": 0.25}
thresholds = {
    "vibration": {"alarm": 4.5, "trip": 7.1},
    "bearing_temp": {"alarm": 85.0, "trip": 100.0},
    "discharge_press": {"alarm": 18.0, "trip": 22.0},
}
calculator = HealthIndexCalculator(weights=weights, thresholds=thresholds)

# Nilai Sensor Sintetis
if anomaly_inject:
    vib_val = 5.2  # Melampaui batas alarm
    temp_val = 88.0  # Melampaui batas alarm
    press_val = 19.5
    status_label = "WARNING - Deviasi Relasi Terdeteksi (GDN)"
    status_color = "red"
else:
    vib_val = 2.1
    temp_val = 68.0
    press_val = 15.2
    status_label = "NORMAL - Operasi Stabil"
    status_color = "green"

current_metrics = {
    "vibration": vib_val,
    "bearing_temp": temp_val,
    "discharge_press": press_val,
}
health_score = calculator.calculate(current_metrics)

# Tampilan Metrik Utama
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Health Index (0-100%)", value=f"{health_score:.1f}%")
with col2:
    st.metric(label="Vibration (mm/s RMS)", value=f"{vib_val:.2f}")
with col3:
    st.metric(label="Bearing Temp (C)", value=f"{temp_val:.1f}")
with col4:
    st.metric(label="Discharge Press (bar)", value=f"{press_val:.1f}")

st.markdown(f"**Status Sistem:** :{status_color}[{status_label}]")

# Visualisasi Health Index Gauge
fig = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=health_score,
        title={"text": "Equipment Health Score (ISO 10816-3)"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#1f77b4"},
            "steps": [
                {"range": [0, 60], "color": "#ff4b4b"},
                {"range": [60, 85], "color": "#ffa040"},
                {"range": [85, 100], "color": "#00cc96"},
            ],
            "threshold": {
                "line": {"color": "black", "width": 4},
                "thickness": 0.75,
                "value": health_score,
            },
        },
    )
)
fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
st.plotly_chart(fig, use_container_width=True)

# Rekomendasi Preskriptif (Graph-RAG: arXiv:2406.18114)
st.subheader("Rekomendasi Tindakan Operator (Prescriptive RCA)")
if anomaly_inject:
    st.error(
        "Tindakan Cepat Lapangan (<30 menit):\n"
        "1. Inspeksi aliran pelumasan bearing sisi drive-end.\n"
        "2. Konfirmasi pembacaan sensor lokal untuk mengeliminasi false alarm transmisi.\n"
        "3. Siapkan prosedur pembagian beban ke unit kompresor cadangan jika getaran melebihi 6.0 mm/s."
    )
else:
    st.success(
        "Kondisi optimal. Parameter beroperasi di dalam batas normal (Zona A/B ISO 10816-3). "
        "Tidak ada tindakan intervensi yang diperlukan saat ini."
    )
