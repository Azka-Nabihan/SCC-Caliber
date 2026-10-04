"""
Chandra Asri Petrochemical - Single Pane of Glass (SPOG) Asset Reliability Platform.
CALIBER 2026 - Case 2: Intelligent Manufacturing.

Zero-Torch Runtime interactive dashboard featuring:
- Tab 1: Executive Cockpit & Strategic ROI (with On-Demand Gemini Copilot)
- Tab 2: Sensor Telemetry & Operational Intervention (Industrial P-F Curve Simulator)
- Tab 3: Plant ZCU Fleet Reliability & Risk Priority Matrix (56 Assets)
"""

import os
from pathlib import Path

# Native .env loader (Stdlib first, zero external dependency - Ponytail Principle)
def _load_env_native():
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    _load_env_native()

import streamlit as st
import pandas as pd

from src.app.data_provider import DashboardDataProvider
from src.app.charts import (
    CHANDRA_THEME,
    create_health_index_gauge,
    create_telemetry_trend_chart,
    create_pid_deviation_graph,
    create_pf_escalation_chart,
)

# Page Configuration (Solution H6: 100% Industrial English UI)
st.set_page_config(
    page_title="Chandra Asri SPOG Platform | CALIBER 2026",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS Styling (Chandra Asri Corporate Theme)
st.markdown(
    """
    <style>
    /* Global Typography & Backgrounds */
    .stApp {
        background-color: #0B1120;
        color: #F8FAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Container */
    .spog-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }
    .spog-title {
        font-size: 26px;
        font-weight: 700;
        color: #F8FAFC;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .spog-subtitle {
        font-size: 13px;
        color: #94A3B8;
        margin-top: 4px;
    }
    
    /* KPI Card Containers */
    .kpi-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px 20px;
        height: 100%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25);
    }
    .kpi-title {
        font-size: 12px;
        text-transform: uppercase;
        font-weight: 600;
        color: #94A3B8;
        letter-spacing: 0.5px;
    }
    .kpi-val {
        font-size: 28px;
        font-weight: 700;
        color: #F8FAFC;
        margin-top: 6px;
    }
    .kpi-sub {
        font-size: 12px;
        color: #38BDF8;
        margin-top: 4px;
    }

    /* Status Alert Badges */
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge-amber {
        background-color: rgba(245, 158, 11, 0.2);
        color: #F59E0B;
        border: 1px solid #F59E0B;
    }
    .badge-green {
        background-color: rgba(16, 185, 129, 0.2);
        color: #10B981;
        border: 1px solid #10B981;
    }
    .badge-yellow {
        background-color: rgba(234, 179, 8, 0.2);
        color: #EAB308;
        border: 1px solid #EAB308;
    }
    .badge-red {
        background-color: rgba(239, 68, 68, 0.2);
        color: #EF4444;
        border: 1px solid #EF4444;
    }
    .badge-grey {
        background-color: rgba(100, 116, 139, 0.2);
        color: #94A3B8;
        border: 1px solid #64748B;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_data_provider() -> DashboardDataProvider:
    return DashboardDataProvider()


def render_header():
    st.markdown(
        """
        <div class="spog-header">
            <div class="spog-title">🏭 Chandra Asri Petrochemical — Single Pane of Glass Platform</div>
            <div class="spog-subtitle">
                <b>CALIBER 2026 (Case 2: Intelligent Manufacturing)</b> | Plant ZCU Asset Reliability & Predictive Decision Engine
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    provider = get_data_provider()
    df = provider.load_timeseries_data()

    # --- SIDEBAR CONTROLLER ---
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/4/4e/Chandra_Asri_Petrochemical_logo.png", width=180) if False else None
    st.sidebar.markdown("### 🎛️ Operator Control Console")

    # Pilot Asset Selector (Solution C5: locked MVP)
    asset_selection = st.sidebar.selectbox(
        "Monitored Asset",
        options=["KO-3201 (Cracked Gas Compressor - ZCU)"],
        index=0,
        help="Pilot Asset MVP with 720h verified telemetry. 56 Plant ZCU fleet assets available in Tab 3.",
    )
    st.sidebar.caption("🔒 *Pilot Asset MVP (56 ZCU assets available in Tab 3)*")

    # Bookmark Quick Jump Buttons (Solutions C6, L2)
    st.sidebar.markdown("#### ⚡ Operational Bookmarks")
    c_bm1, c_bm2 = st.sidebar.columns(2)
    c_bm3, c_bm4 = st.sidebar.columns(2)

    # Initialize current hour in session state
    if "selected_hour" not in st.session_state:
        st.session_state.selected_hour = 633

    if c_bm1.button("Hr 100: Normal", use_container_width=True, help="Baseline steady-state operation"):
        st.session_state.selected_hour = 100
    if c_bm2.button("Hr 633: GDN Alert", use_container_width=True, help="AI Early Warning: 16h before DCS alarm"):
        st.session_state.selected_hour = 633
    if c_bm3.button("Hr 649: DCS Alarm", use_container_width=True, help="Conventional 45 um threshold reached"):
        st.session_state.selected_hour = 649
    if c_bm4.button("Hr 679: Trip Post", use_container_width=True, help="Actual machine trip (RUN_STATUS=0)"):
        st.session_state.selected_hour = 679

    # Timeline Interactive Slider (Solution L2: 0..719)
    current_hour = st.sidebar.slider(
        "Operational Timeline (Hours)",
        min_value=0,
        max_value=719,
        value=int(st.session_state.selected_hour),
        key="timeline_slider",
        help="Simulate chronological time travel from Hour 0 to Hour 719.",
    )
    st.session_state.selected_hour = current_hour

    # Retrieve real-time snapshot
    snap = provider.get_hour_snapshot(current_hour)

    # Sidebar Status Indicator (Solution C2)
    st.sidebar.markdown("---")
    badge_class = f"badge-{snap['status_color'].lower()}"
    st.sidebar.markdown(
        f"**Live Asset Status:**<br><span class='badge-pill {badge_class}'>{snap['current_status'].split(',')[0]}</span>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(f"**Vibration:** `{snap['vibration']:.2f} µm` (Alarm: 45 µm | Trip: 75 µm)")
    st.sidebar.markdown(f"**Health Index:** `{snap['health_index']:.1f}%`")
    st.sidebar.caption("⚡ *Zero-Torch In-Memory Engine: <2 ms lookup*")

    # Render Main Header
    render_header()

    # --- 3-TAB APPLICATION STRUCTURE ---
    tab1, tab2, tab3 = st.tabs([
        "📊 Tab 1: Executive Cockpit & Strategic ROI",
        "📈 Tab 2: Sensor Telemetry & Operational Intervention (P-F Curve)",
        "🌐 Tab 3: Plant ZCU Fleet Reliability & Risk Priority Matrix",
    ])

    # =========================================================================
    # TAB 1: EXECUTIVE COCKPIT & STRATEGIC ROI
    # =========================================================================
    with tab1:
        # Row 1: Hero Metric Cards (Solutions C2, C3, C4)
        c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.3, 1.5])

        with c1:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Operational Status</div>
                    <div style="margin-top:12px;"><span class="badge-pill {badge_class}">{snap['current_status'].split(',')[0]}</span></div>
                    <div class="kpi-sub" style="margin-top:10px;">Run State: {'RUNNING' if snap['run_status']==1 else 'STOPPED / TRIP'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c2:
            st.plotly_chart(
                create_health_index_gauge(snap["health_index"], snap["status_color"], snap["operational_state"]),
                use_container_width=True,
            )

        with c3:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Early Detection Lead Time</div>
                    <div class="kpi-val" style="color:#38BDF8;">16 Hours</div>
                    <div class="kpi-sub">Ahead of DCS Alarm 45 µm (46h before Trip)</div>
                    <div style="font-size:11px; color:#94A3B8; margin-top:8px;">Secondary: 32h before legacy 60 µm alert</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c4:
            physics_savings = snap["financial_risk_dual_metric"].get("forward_looking_process_simulation", {}).get("potential_cost_savings_k_usd", 1188.0)
            hist_ref = snap["financial_risk_dual_metric"].get("historical_benchmark_retrospective", {})
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Strategic Financial ROI</div>
                    <div class="kpi-val" style="color:#10B981;">${physics_savings:,.1f}k USD</div>
                    <div class="kpi-sub">[PROCESS PHYSICS: (32-8h) × 55 T/H × $900/t]</div>
                    <div style="font-size:11px; color:#E2E8F0; margin-top:6px; background:rgba(255,255,255,0.06); padding:4px 8px; border-radius:4px;">
                        🏛️ Historical Benchmark: <b>{hist_ref.get('incident_reference', 'AR-2026-ZCU-0142')}</b> (${hist_ref.get('actual_loss_k_usd', 1584.0):,.1f}k actual loss)
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Row 2: Executive Shift Briefing & On-Demand Copilot (Solutions H1, H2, L5)
        st.markdown("### 🤖 Operational Copilot — Executive Shift Briefing")
        briefing_col1, briefing_col2 = st.columns([3.5, 1.2])

        # State management for on-demand Gemini generation
        if "gemini_briefing" not in st.session_state:
            st.session_state.gemini_briefing = None
        if "gemini_hour" not in st.session_state:
            st.session_state.gemini_hour = None

        with briefing_col2:
            st.markdown("**AI Synthesis Mode:**")
            gen_btn = st.button("⚡ Generate AI Briefing via Gemini", use_container_width=True, help="Call Google Gemini 1.5 Pro to synthesize natural-language shift briefing.")
            if gen_btn:
                with st.spinner("Synthesizing Executive Shift Briefing via Gemini API..."):
                    llm_card = provider.recommender.generate_action_card(
                        tag_number="KO-3201",
                        anomaly_info=snap,
                        use_llm=True,
                    )
                    st.session_state.gemini_briefing = llm_card["copilot_shift_briefing"]
                    st.session_state.gemini_mode = llm_card["synthesis_mode"]
                    st.session_state.gemini_hour = current_hour

        with briefing_col1:
            if st.session_state.gemini_briefing and st.session_state.gemini_hour == current_hour:
                active_briefing = st.session_state.gemini_briefing
                active_mode = st.session_state.gemini_mode
            else:
                active_briefing = snap["copilot_shift_briefing"]
                active_mode = snap["synthesis_mode"]

            st.info(f"**Briefing Log:** {active_briefing}")
            st.caption(f"🔧 Mode: `{active_mode}`")

        st.markdown("---")

        # Row 3: Prescriptive Actions & Permanent CAPA Tracking
        st.markdown("### 📋 Prescriptive Mitigation & Engineering CAPA Console")
        act_col1, act_col2 = st.columns(2)

        with act_col1:
            st.markdown("#### ⚡ Immediate Operator Actions (< 30 Mins)")
            for act in snap["immediate_actions"]:
                st.markdown(
                    f"""
                    <div style="background:#1E293B; border-left:4px solid #38BDF8; padding:10px 14px; margin-bottom:8px; border-radius:4px;">
                        <b>Step {act.get('step', 1)}:</b> {act.get('action', '')}
                        <div style="font-size:11px; color:#94A3B8; margin-top:4px;">
                            ⏱️ <i>Timeframe: {act.get('timeframe', '< 30 min')}</i> &nbsp;|&nbsp; 🏷️ <b>Source: {act.get('source', 'RCA-2')}</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with act_col2:
            st.markdown("#### 🛡️ Permanent Engineering CAPA Tracker")
            for capa in snap["permanent_capa"][:4]:
                st.markdown(
                    f"""
                    <div style="background:#1E293B; border-left:4px solid #10B981; padding:10px 14px; margin-bottom:8px; border-radius:4px;">
                        <b>{capa.get('category', 'Technical CAPA')}:</b> {capa.get('action', '')}
                        <div style="font-size:11px; color:#94A3B8; margin-top:4px;">
                            👤 PIC: <b>{capa.get('pic', 'Reliability Team')}</b> &nbsp;|&nbsp; 📅 Due: <b>{capa.get('due_date', '2026-05-30')}</b> &nbsp;|&nbsp; 🏷️ <b>{capa.get('source', 'Official RCA')}</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("---")

        # Row 4: Similar Historical Incidents Table (Solution H7)
        st.markdown("### 🔍 Cross-Silo Similar Incidents Retrieval (Enterprise Memory)")
        st.caption("Top matching historical failures across 380 refinery and petrochemical incident records:")
        similar_incs = provider.get_similar_incidents(equipment_type="COMPRESSOR", top_k=3)
        sim_df = pd.DataFrame(similar_incs).rename(columns={
            "incident_reference": "Incident No",
            "plant": "Plant",
            "tag_number": "Asset Tag",
            "equipment": "Title / Subsystem",
            "failure_mechanism": "Damage Mechanism",
            "actual_downtime_hrs": "Downtime (Hrs)",
            "actual_loss_k_usd": "Loss ($k USD)",
            "total_loss_k_usd": "Total ($k USD)",
        })
        st.dataframe(sim_df, use_container_width=True, hide_index=True)

    # =========================================================================
    # TAB 2: SENSOR TELEMETRY & OPERATIONAL INTERVENTION (P-F CURVE)
    # =========================================================================
    with tab2:
        st.markdown("### 📈 Real-Time Sensor Telemetry & Anomaly Attribution")
        st.caption("Multimodal telemetry streams from OSIsoft PI integration correlated with Graph Deviation Network (GDN) scores:")

        # Multi-sensor trend chart (Solution C6)
        st.plotly_chart(create_telemetry_trend_chart(df, current_hour), use_container_width=True)

        # Educational Annotation on Upstream Stability (Solution M7)
        st.markdown(
            """
            <div style="background:#1E293B; border-left:4px solid #A855F7; padding:10px 16px; border-radius:6px; margin-bottom:16px;">
                💡 <b>Engineering Insight on GDN Detection at Hour 633:</b> Upstream process variables (<i>Plant Rate: 56.3 T/H, Feed Flow: 55.4 T/H, Bearing Temp: 64.5 °C</i>) remain perfectly steady within normal design envelopes. The GDN anomaly score (10.72) is strictly isolated to localized shaft micro-vibration deviation, confirming an internal mechanical lube-oil degradation mechanism rather than furnace cracking instability.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Row 2: Topological P&ID Graph (Solution H4)
        st.markdown("### 🗺️ P&ID Sensor Topology & Dynamic Correlation Deviation")
        pid_col, pf_summary_col = st.columns([1.8, 1.2])

        with pid_col:
            st.plotly_chart(create_pid_deviation_graph(snap["top_contributors"], current_hour), use_container_width=True)

        with pf_summary_col:
            st.markdown("#### 🔍 Active Contributors at Current Hour")
            st.write(f"**Current Hour:** `{current_hour}` ({snap['timestamp']})")
            st.write(f"**Active Status:** `{snap['current_status'].split(',')[0]}`")
            st.write(f"**GDN Anomaly Score:** `{snap['gdn_anomaly_score']:.2f}` (Threshold: 3.11)")
            st.write("**Top Contributing Nodes:**")
            if snap["top_contributors"]:
                for node, score in snap["top_contributors"]:
                    st.markdown(f"- **`{node}`**: Local Deviation Score `{score:.2f}`")
            else:
                st.markdown("- *All sensor correlation scores within baseline variance.*")

        st.markdown("---")

        # Row 3: Industrial P-F Curve Decision Simulator (Solutions C1, H3)
        st.markdown("### ⏱️ Industrial P-F Curve Decision Escalation Simulator")
        st.caption("Interactive What-If analysis evaluating the economic cost of delayed operational turnaround:")

        # Simulator slider
        sim_hour = st.slider(
            "Controlled Turnaround Decision Hour (t_action)",
            min_value=633,
            max_value=679,
            value=max(633, min(679, current_hour)),
            key="pf_sim_slider",
            help="Evaluate impact of intervention timing along the P-F curve degradation interval (Hour 633 to Hour 679).",
        )

        sim_res = provider.simulate_pf_decision(action_hour=sim_hour)

        # Simulator KPI cards
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Intervention Hour", f"Hr {sim_res['action_hour']}", f"+{sim_res['delay_from_detection_hrs']}h Delay")
        sc2.metric("Projected Turnaround", f"{sim_res['projected_downtime_hrs']:.1f} Hours", "vs 32h Unplanned Trip")
        sc3.metric("Cost of Delay", f"${sim_res['cost_of_delay_k_usd']:,.1f}k", f"@ ${sim_res['loss_per_delay_hour_k_usd']:.1f}k/hr")
        sc4.metric("Net Cost Savings", f"${sim_res['net_savings_k_usd']:,.1f}k USD", f"vs ${sim_res['uncontrolled_trip_loss_k_usd']:,.1f}k Loss", delta_color="normal")

        # P-F Degradation Chart
        st.plotly_chart(create_pf_escalation_chart(sim_hour), use_container_width=True)

        with st.expander("ℹ️ Engineering Assumption & Turnaround Protocol Justification (ISO 14224 / API 581)"):
            st.markdown(
                """
                - **Planned Controlled Shutdown Baseline (8 Hours) [ENGINEERING ASSUMPTION]:**
                  - **2 Hours**: Controlled furnace rate ramp-down, plant train depressurization, and compressor cooling.
                  - **4 Hours**: Babbitt insert journal bearing replacement and lube-oil flushing with clean ISO VG 46 synthetic lubricant.
                  - **2 Hours**: Gradual machine spin-up, heat synchronization, and ramp back to full 55.0 T/H cracking capacity.
                - **Unplanned Machine Trip Baseline (32 Hours) [FACT - RCA-2 / AR-2026-ZCU-0142]:**
                  - Catastrophic rotor contact and bearing wipe-out required extensive casing disassembly, shaft realignment, and emergency turnaround.
                """
            )

    # =========================================================================
    # TAB 3: PLANT ZCU FLEET RELIABILITY & RISK PRIORITY MATRIX
    # =========================================================================
    with tab3:
        st.markdown("### 🌐 Plant ZCU Fleet Reliability & Risk Priority Matrix")
        st.caption("Comprehensive asset health, failure modes, and enterprise risk exposure across all 56 Plant ZCU equipments:")

        fleet_meta = provider.get_fleet_matrix()

        # Row 1: Enterprise Exposure Banners (Solutions C4, M3, M4)
        fc1, fc2, fc3, fc4 = st.columns(4)
        fc1.metric("Plant ZCU Portfolio Risk", f"${fleet_meta['zcu_portfolio_risk_k_usd']/1000.0:.2f}M USD", f"{fleet_meta['zcu_incident_count']} Incidents (Rank #1)")
        fc2.metric("12-Plant Complex Exposure", f"${fleet_meta['complex_total_exposure_k_usd']/1000.0:.2f}M USD", f"{fleet_meta['complex_incident_count']} Total Incidents")
        fc3.metric("Monitored ZCU Assets", f"{fleet_meta['total_assets']} Equipment", "17 Rotary | 10 Elec | 29 Static")
        fc4.metric("Data Provenance Ratio", "2 FACT : 54 HYPOTHESIS", "Official RCAs vs FMEA Engineering")

        st.markdown("---")

        # Row 2: Interactive Filters (Solutions M3, H7)
        filt_c1, filt_c2, filt_c3, filt_c4 = st.columns(4)
        with filt_c1:
            cat_filter = st.selectbox("Equipment Discipline", ["All (56)", "Rotary (17)", "Electrical (10)", "Static (29)"])
        with filt_c2:
            class_filter = st.selectbox("Criticality Class", ["All", "Class A", "Class B", "Class C"])
        with filt_c3:
            prio_filter = st.selectbox("Risk Priority", ["All", "P1 - High Priority", "P2 - Medium Priority", "P3 - Routine"])
        with filt_c4:
            prov_filter = st.selectbox("Data Provenance", ["All", "FACT", "ENGINEERING_HYPOTHESIS"])

        # Filter assets
        filtered_assets = fleet_meta["assets"]
        if "Rotary" in cat_filter:
            filtered_assets = [a for a in filtered_assets if a["category"] == "ROTARY"]
        elif "Electrical" in cat_filter:
            filtered_assets = [a for a in filtered_assets if a["category"] == "ELECTRICAL"]
        elif "Static" in cat_filter:
            filtered_assets = [a for a in filtered_assets if a["category"] == "STATIC"]

        if class_filter != "All":
            filtered_assets = [a for a in filtered_assets if class_filter in a["criticality_class"]]
        if prio_filter != "All":
            filtered_assets = [a for a in filtered_assets if prio_filter in a["risk_priority"]]
        if prov_filter != "All":
            filtered_assets = [a for a in filtered_assets if a["provenance_level"] == prov_filter]

        # Display Fleet Table (Solutions M3, L4)
        table_df = pd.DataFrame(filtered_assets).rename(columns={
            "tag_number": "Tag Number",
            "equipment_name": "Equipment Name",
            "category": "Discipline",
            "criticality_class": "Class",
            "dominant_failure_mode": "Dominant Damage Mechanism",
            "typical_downtime_hrs": "Typical Downtime (h)",
            "historical_loss_k_usd": "Historical Impact ($k USD)",
            "risk_score": "Risk Score",
            "risk_priority": "Priority Badge",
            "provenance_level": "Data Provenance",
        })

        st.dataframe(
            table_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Historical Impact ($k USD)": st.column_config.NumberColumn(format="$%.1f k"),
                "Risk Score": st.column_config.NumberColumn(format="%.1f"),
            },
        )
        st.caption(f"Displaying **{len(table_df)}** of **{fleet_meta['total_assets']}** Plant ZCU assets.")


if __name__ == "__main__":
    main()
