"""
Chandra Asri Petrochemical — Plant ZCU Predictive Reliability & Condition Monitoring System.
Condition-Based Maintenance (CBM) Console for CALIBER 2026.
4-Tab Industrial Architecture:
- Tab 1: Asset Overview & Live Alerts
- Tab 2: Sensors & Process Diagram
- Tab 3: Maintenance Tasks & Work Orders
- Tab 4: Plant Assets & Failure Analysis
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path when deployed on Streamlit Cloud
root_dir = Path(__file__).resolve().parents[2]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

from src.app.data_provider import DashboardDataProvider
from src.app.charts import (
    CHANDRA_THEME,
    create_health_index_gauge,
    create_compact_vibration_trend,
    create_telemetry_trend_chart,
    create_process_mimic_chart,
    create_pf_escalation_chart,
)

# Page Configuration (Industrial English UI, Clean Standards)
st.set_page_config(
    page_title="Chandra Asri Plant ZCU Condition Monitoring | CALIBER 2026",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Industrial CSS Styling (Flat DCS Slate Theme, Zero Emojis)
st.markdown(
    """
    <style>
    /* Global Typography & Slate Theme */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* DCS Console Header */
    .dcs-header {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 14px 20px;
        margin-bottom: 16px;
    }
    .dcs-title {
        font-size: 20px;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: -0.3px;
        margin: 0;
    }
    .dcs-subtitle {
        font-size: 12px;
        color: #94A3B8;
        margin-top: 4px;
        font-family: 'Inter', monospace;
    }
    
    /* High-Density Card Panels */
    .cbm-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 12px 16px;
        height: 100%;
    }
    .cbm-label {
        font-size: 11px;
        text-transform: uppercase;
        font-weight: 600;
        color: #94A3B8;
        letter-spacing: 0.5px;
    }
    .cbm-val {
        font-size: 24px;
        font-weight: 700;
        color: #F8FAFC;
        margin-top: 4px;
    }
    .cbm-sub {
        font-size: 11px;
        color: #38BDF8;
        margin-top: 3px;
    }
    
    /* ISA-18.2 Alarm & State Status Badges */
    .isa-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-family: 'Inter', monospace;
    }
    .isa-normal {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid #10B981;
    }
    .isa-amber {
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid #F59E0B;
    }
    .isa-yellow {
        background-color: rgba(234, 179, 8, 0.15);
        color: #EAB308;
        border: 1px solid #EAB308;
    }
    .isa-red {
        background-color: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid #EF4444;
    }
    .isa-grey {
        background-color: rgba(100, 116, 139, 0.15);
        color: #94A3B8;
        border: 1px solid #64748B;
    }

    /* Industrial Action & CAPA Items */
    .action-item {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-left: 3px solid #38BDF8;
        padding: 8px 12px;
        margin-bottom: 6px;
        border-radius: 4px;
        font-size: 12px;
    }
    .capa-item {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-left: 3px solid #10B981;
        padding: 8px 12px;
        margin-bottom: 6px;
        border-radius: 4px;
        font-size: 12px;
    }

    /* Diagnostic CoT Stepper Cards */
    .diag-stage {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 4px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .diag-header {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        color: #38BDF8;
        margin-bottom: 4px;
        font-family: 'Inter', monospace;
    }
    .diag-body {
        font-size: 12px;
        color: #F8FAFC;
        line-height: 1.5;
    }

    /* KPI Cards inside P-F Grid */
    .grid-kpi-static {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-top: 10px;
    }
    .kpi-box-static {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 4px;
        padding: 10px 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_data_provider() -> DashboardDataProvider:
    return DashboardDataProvider()


def render_header():
    st.markdown(
        """
        <div class="dcs-header">
            <div class="dcs-title">Chandra Asri Petrochemical — Plant ZCU Condition Monitoring & Reliability Console</div>
            <div class="dcs-subtitle">
                CALIBER 2026 (Case 2: Intelligent Manufacturing) | Process Area: Plant ZCU Olefins Cracking Train
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    provider = get_data_provider()
    df = provider.load_timeseries_data()
    fleet_meta = provider.get_fleet_matrix()
    all_assets = fleet_meta["assets"]

    # --- SIDEBAR OPERATOR CONSOLE ---
    st.sidebar.markdown("### Operator Control Console")

    # Build 56-asset options list: KO-3201 first, remaining 55 sorted alphabetically
    pilot_label = "KO-3201 - Cracked Gas Compressor"
    other_labels = sorted([
        f"{a['tag_number']} - {a['equipment_name']}"
        for a in all_assets
        if a["tag_number"] != "KO-3201"
    ])
    asset_options = [pilot_label] + other_labels

    if "selected_asset" not in st.session_state:
        st.session_state.selected_asset = pilot_label

    try:
        current_asset_idx = asset_options.index(st.session_state.selected_asset)
    except ValueError:
        current_asset_idx = 0

    selected_asset = st.sidebar.selectbox(
        "Monitored Asset",
        options=asset_options,
        index=current_asset_idx,
        help="Pilot Asset KO-3201 has continuous 720h verified telemetry. All 56 Plant ZCU equipment are cataloged in Tab 4.",
    )
    st.session_state.selected_asset = selected_asset
    st.sidebar.caption("(56 Plant Assets in Tab 4)")

    # Operational Timeline Bookmarks (Short, un-truncated button labels)
    st.sidebar.markdown("#### Operational Bookmarks")
    c_bm1, c_bm2 = st.sidebar.columns(2)
    c_bm3, c_bm4 = st.sidebar.columns(2)

    if "timeline_slider" not in st.session_state:
        st.session_state.timeline_slider = 633

    if c_bm1.button("Hr 100: Normal", use_container_width=True, help="Baseline steady-state operation"):
        st.session_state.timeline_slider = 100
        st.rerun()
    if c_bm2.button("Hr 633: Alert", use_container_width=True, help="Early Warning: 16h before DCS alarm"):
        st.session_state.timeline_slider = 633
        st.rerun()
    if c_bm3.button("Hr 649: Alarm", use_container_width=True, help="Conventional 45 um alarm threshold reached"):
        st.session_state.timeline_slider = 649
        st.rerun()
    if c_bm4.button("Hr 679: Trip", use_container_width=True, help="Actual machine trip (RUN_STATUS=0)"):
        st.session_state.timeline_slider = 679
        st.rerun()

    # Timeline Interactive Slider (0..719)
    current_hour = st.sidebar.slider(
        "Operational Timeline (Hours)",
        min_value=0,
        max_value=719,
        key="timeline_slider",
        help="Chronological time travel from Hour 0 to Hour 719.",
    )

    # Retrieve telemetry snapshot
    snap = provider.get_hour_snapshot(current_hour)

    # Sidebar Status Indicator (Clean ISA badge, repeated numbers removed)
    st.sidebar.markdown("---")
    badge_map = {
        "GREEN": "isa-normal",
        "AMBER": "isa-amber",
        "YELLOW": "isa-yellow",
        "RED": "isa-red",
        "GREY": "isa-grey",
    }
    badge_css = badge_map.get(snap["status_color"].upper(), "isa-normal")

    st.sidebar.markdown(
        f"**Condition Status:**<br><span class='isa-badge {badge_css}'>{snap['current_status'].split(',')[0]}</span>",
        unsafe_allow_html=True,
    )

    # Sidebar Footer: Team Azkaban Credits
    st.sidebar.markdown(
        """
        <div style="background:#1E293B; border:1px solid #334155; border-radius:6px; padding:12px; margin-top:24px; font-size:11px;">
            <div style="font-weight:700; color:#38BDF8; letter-spacing:0.5px; font-size:10px;">DEVELOPED FOR CALIBER 2026</div>
            <div style="font-weight:700; color:#F8FAFC; margin-top:4px; font-size:12px;">Team Azkaban</div>
            <div style="color:#94A3B8; margin-top:4px; line-height:1.4;">
                • Azka Nabihan H.<br>
                • Nabila Najlaa C.<br>
                • Rasiendriya Sajna
            </div>
            <div style="color:#64748B; margin-top:6px; font-size:10px;">Case 2: Intelligent Manufacturing</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render Main Header
    render_header()

    # Non-Pilot Asset Informative Notification Banner
    is_pilot = selected_asset.startswith("KO-3201")
    if not is_pilot:
        st.info(
            f"Asset Status: NORMAL STEADY. High-frequency 720-hour time-travel simulation is currently active for Pilot Asset KO-3201. "
            f"Full risk profile, failure history, and equipment criticality for {selected_asset} are displayed in Tab 4 (Plant Assets & Failure Analysis)."
        )
        if st.button("Switch Back to Pilot Asset KO-3201", type="primary"):
            st.session_state.selected_asset = pilot_label
            st.rerun()

    # --- 4-TAB APPLICATION STRUCTURE ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "Tab 1: Asset Overview & Live Alerts",
        "Tab 2: Sensors & Process Diagram",
        "Tab 3: Maintenance Tasks & Work Orders",
        "Tab 4: Plant Assets & Failure Analysis",
    ])

    # =========================================================================
    # TAB 1: ASSET OVERVIEW & LIVE ALERTS
    # =========================================================================
    with tab1:
        # Row 1: Executive KPI Metrics (4 Cards)
        c1, c2, c3, c4 = st.columns([1.1, 1.2, 1.2, 1.5])

        with c1:
            st.markdown(
                f"""
                <div class="cbm-card">
                    <div class="cbm-label">Operating Condition</div>
                    <div style="margin-top:10px;"><span class="isa-badge {badge_css}">{snap['current_status'].split(',')[0]}</span></div>
                    <div class="cbm-sub" style="margin-top:8px;">Machine State: {'RUNNING' if snap['run_status']==1 else 'STOPPED / TRIP'}</div>
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
                <div class="cbm-card">
                    <div class="cbm-label">Early Warning Lead Time</div>
                    <div class="cbm-val" style="color:#38BDF8;">16 Hours</div>
                    <div class="cbm-sub">Ahead of DCS Alarm 45 µm (46h before Trip)</div>
                    <div style="font-size:10px; color:#64748B; margin-top:6px;">Baseline: 32h ahead of legacy 60 µm alert</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with c4:
            physics_savings = snap["financial_risk_dual_metric"].get("forward_looking_process_simulation", {}).get("potential_cost_savings_k_usd", 1188.0)
            hist_ref = snap["financial_risk_dual_metric"].get("historical_benchmark_retrospective", {})
            st.markdown(
                f"""
                <div class="cbm-card">
                    <div class="cbm-label">Intervention Economic Impact</div>
                    <div class="cbm-val" style="color:#10B981;">${physics_savings:,.1f}k USD</div>
                    <div class="cbm-sub">Avoided Loss: (32h - 8h Turnaround) × 55 T/H × $900/ton</div>
                    <div style="font-size:10px; color:#94A3B8; margin-top:6px; background:#0F172A; padding:3px 6px; border-radius:3px; border:1px solid #334155;">
                        Historical Incident Ref: <b>{hist_ref.get('incident_reference', 'AR-2026-ZCU-0142')}</b> (${hist_ref.get('actual_loss_k_usd', 1584.0):,.1f}k actual loss)
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)

        # Operational Status Banner
        if snap["operational_state"] == 3:
            st.info(
                f"EARLY WARNING ACTIVE (Hour {current_hour}): Shaft vibration micro-deviation detected "
                f"(VI-3201: {snap['vibration']:.2f} µm, GDN score: {snap['gdn_anomaly_score']:.2f}). "
                "16-hour proactive intervention window active. Refer to Tab 3 for maintenance work order and SOP steps."
            )
        elif snap["operational_state"] in [4, 5]:
            st.warning(
                f"ALARM LEVEL EXCEEDED (Hour {current_hour}): Shaft radial vibration has reached {snap['vibration']:.2f} µm "
                "(exceeding DCS Alarm threshold 45 µm). Immediate controlled mitigation required. Refer to Tab 3."
            )
        elif snap["operational_state"] == 1:
            st.error(
                f"MACHINE OFFLINE / TRIP (Hour {current_hour}): Cracked gas compressor stopped (RUN_STATUS = 0). "
                "Emergency turnaround and overhaul protocol active. Refer to Tab 3."
            )
        else:
            st.success(
                f"NORMAL STEADY-STATE (Hour {current_hour}): All monitored telemetry and process variables are within design baseline limits."
            )

        # Row 2: Clean 2-Column Split Console
        col_left, col_right = st.columns([1.3, 1.1])

        # --- LEFT COLUMN: SHAFT VIBRATION TREND & SAFETY LIMITS ---
        with col_left:
            st.markdown("#### Shaft Vibration Trend vs DCS Alarm Thresholds")
            st.plotly_chart(create_compact_vibration_trend(df, current_hour), use_container_width=True)
            st.caption(
                "Operational Thresholds: Normal Baseline (< 30.0 µm) | Early Alert (31.24 µm at Hr 633) | "
                "DCS High Alarm (45.0 µm) | DCS High-High Trip (75.0 µm)"
            )

        # --- RIGHT COLUMN: OPERATIONAL ASSISTANT (WHAT-IF COPILOT) ---
        with col_right:
            st.markdown("#### Operational Assistant (What-If Copilot)")
            st.caption("Ask questions and simulate engineering scenarios against verified plant knowledge:")

            # 3 Preset Action Buttons
            p_col1, p_col2, p_col3 = st.columns(3)
            selected_query = None

            if p_col1.button("Simulate 10% Rate Cut", use_container_width=True, help="Simulate extending lead time via load reduction"):
                selected_query = "Simulasi penurunan laju alir 10% pada kompresor"
            if p_col2.button("Babbitt Wipe-Out Risk", use_container_width=True, help="Assess mechanical catastrophic risk if run unmitigated"):
                selected_query = "Analisis risiko catastrophic babbitt wipe-out jika mesin dipaksa beroperasi"
            if p_col3.button("Shutdown Protocol (8h)", use_container_width=True, help="Step-by-step controlled shutdown SOP"):
                selected_query = "Prosedur urutan controlled shutdown 8 jam terencana"

            custom_q = st.text_input(
                "Ask Copilot a Custom Operational Question:",
                placeholder="e.g. What is the safe operating temperature for cooler HE-3301?",
                key="copilot_custom_query",
            )
            if custom_q.strip():
                selected_query = custom_q.strip()

            if "copilot_active_query" not in st.session_state:
                st.session_state.copilot_active_query = "Simulasi penurunan laju alir 10% pada kompresor"

            if selected_query:
                st.session_state.copilot_active_query = selected_query

            # Execute Copilot Simulation
            active_q = st.session_state.copilot_active_query
            copilot_res = provider.run_copilot_simulation(active_q, current_hour)

            engine_status = copilot_res.get("engine_status", "OFFLINE_FALLBACK")
            if engine_status == "LIVE_ONLINE":
                badge_html = '<span style="background:rgba(16,185,129,0.15); color:#10B981; border:1px solid #10B981; padding:2px 8px; border-radius:3px; font-size:10px; font-weight:700; letter-spacing:0.5px;">LIVE PROCESS COPILOT (ONLINE CLOUD MODE)</span>'
                border_accent = "#10B981"
            else:
                badge_html = '<span style="background:rgba(148,163,184,0.15); color:#94A3B8; border:1px solid #475569; padding:2px 8px; border-radius:3px; font-size:10px; font-weight:700; letter-spacing:0.5px;">DETERMINISTIC RULE ENGINE (0 MS OFFLINE FALLBACK)</span>'
                border_accent = "#818CF8"

            st.markdown(
                f"""
                <div style="background:#1E293B; border:1px solid #334155; border-left:3px solid {border_accent}; border-radius:4px; padding:12px 14px; font-size:12px; margin-top:8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; border-bottom:1px solid #334155; padding-bottom:6px;">
                        <div style="font-weight:700; color:{border_accent}; font-size:11px; text-transform:uppercase;">
                            {copilot_res['scenario_title']}
                        </div>
                        <div>
                            {badge_html}
                        </div>
                    </div>
                    <div style="color:#F8FAFC; line-height:1.5; white-space:pre-line;">
                        {copilot_res['answer']}
                    </div>
                    <div style="font-size:10px; color:#64748B; margin-top:8px; border-top:1px solid #334155; padding-top:4px;">
                        Grounding Source: <i>{copilot_res['source']}</i>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)

        # AI Root Cause Diagnostic Reasoning Engine Card
        diag = provider.get_diagnostic_reasoning(current_hour)
        st.markdown("#### AI Root Cause Diagnostic Reasoning Engine (Multi-Modal Chain-of-Thought)")
        st.markdown(
            f"""
            <div style="background:#1E293B; border:1px solid #334155; border-radius:6px; padding:14px 16px; margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; border-bottom:1px solid #334155; padding-bottom:8px;">
                    <div style="font-size:12px; font-weight:700; color:#38BDF8; font-family:'Inter', monospace;">
                        AUTONOMOUS DIAGNOSTIC INFERENCE | ASSET TAG: KO-3201 | HOUR {current_hour}
                    </div>
                    <div>
                        <span class="isa-badge isa-amber">CONFIDENCE: {diag['confidence_score']:.1f}%</span>
                        &nbsp;<span class="isa-badge isa-normal">MATCH: {diag['matched_incident']}</span>
                    </div>
                </div>
                <div class="diag-stage" style="border-left:3px solid #38BDF8;">
                    <div class="diag-header">Stage 1: Multi-Sensor Telemetry Observation</div>
                    <div class="diag-body">{diag['step_1_observation']}</div>
                </div>
                <div class="diag-stage" style="border-left:3px solid #F59E0B;">
                    <div class="diag-header" style="color:#F59E0B;">Stage 2: Mechanical & Thermodynamic Process Inference</div>
                    <div class="diag-body">{diag['step_2_inference']}</div>
                </div>
                <div class="diag-stage" style="border-left:3px solid #10B981;">
                    <div class="diag-header" style="color:#10B981;">Stage 3: Enterprise RCA Memory Cross-Correlation</div>
                    <div class="diag-body">{diag['step_3_rca_correlation']}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # =========================================================================
    # TAB 2: SENSORS & PROCESS DIAGRAM
    # =========================================================================
    with tab2:
        st.markdown("### Process Instrumentation Telemetry & Anomaly Attribution")
        st.caption("Continuous 720-hour OSIsoft PI telemetry streams synchronized with Graph Deviation Network (GDN) multimodal anomaly scores:")

        # Two-tier telemetry chart
        st.plotly_chart(create_telemetry_trend_chart(df, current_hour), use_container_width=True)

        st.markdown(
            f"""
            <div style="background:#1E293B; border:1px solid #334155; border-left:3px solid #818CF8; padding:10px 14px; border-radius:4px; font-size:12px; margin-bottom:14px;">
                <b>Engineering Diagnostic Note (Hour {current_hour}):</b> Upstream process conditions (<i>Plant Rate: 56.3 T/H, Feed Flow: 55.4 T/H, Bearing Temp: 64.5 °C</i>) remain within stable design envelopes. The GDN anomaly score ({snap['gdn_anomaly_score']:.2f}) is localized to shaft radial vibration micro-deviation, confirming early babbitt bearing distress rather than process instability.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Authentic 2-Loop Process P&ID Mimic Diagram (ISA-5.1)
        st.markdown("### Plant ZCU 2-Loop Process P&ID Diagram (Gas Cracking Train + Lube Auxiliary System)")
        st.caption("Top Loop: Main Cracked Gas Stream with Anti-Surge Recycle line. Bottom Loop: Closed Lube Oil Cooling Circuit (HE-3301 feeding KO-3201 bearing).")
        st.plotly_chart(
            create_process_mimic_chart(
                snap["top_contributors"],
                current_hour,
                snap["vibration"],
            ),
            use_container_width=True,
        )

    # =========================================================================
    # TAB 3: MAINTENANCE TASKS & WORK ORDERS
    # =========================================================================
    with tab3:
        st.markdown("### Enterprise Maintenance Tasks & Work Orders (SAP PM)")
        st.caption("Dynamic timeline adaptation: Work order priority, status, and action steps automatically update with operational state.")

        # Dynamically retrieve work order payload for the current hour
        sap_data = provider.generate_sap_work_order(current_hour)

        col_wo, col_sop = st.columns([1.2, 1.0])

        with col_wo:
            st.markdown("#### SAP Plant Maintenance Work Order Ticket")
            st.markdown(
                f"""
                <div style="background:#0F172A; border:1px solid #38BDF8; border-radius:6px; padding:14px 16px; margin-bottom:14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; padding-bottom:8px; margin-bottom:10px;">
                        <div style="font-weight:700; font-size:13px; color:#38BDF8; font-family:'Inter', monospace;">
                            ORDER: {sap_data['work_order_id']}
                        </div>
                        <span class="isa-badge isa-normal">{sap_data['status']}</span>
                    </div>
                    <div style="font-size:12px; line-height:1.7; color:#F8FAFC;">
                        • <b>Notification:</b> <code>{sap_data['notification_id']}</code><br>
                        • <b>Order Type:</b> <code>{sap_data['order_type']}</code><br>
                        • <b>Functional Location:</b> <code>{sap_data['functional_location']}</code><br>
                        • <b>Asset Description:</b> {sap_data['asset_description']}<br>
                        • <b>Priority:</b> <span style="color:#EF4444; font-weight:700;">{sap_data['priority']}</span><br>
                        • <b>Target Duration:</b> {sap_data['target_duration_hrs']} Hours | Lead Window: {sap_data['required_window']}<br>
                        • <b>Assigned Crew:</b> {sap_data['lead_technician']} ({sap_data['work_center']})<br>
                        • <b>Permit-to-Work:</b> <code>{sap_data['safety_permit']}</code>
                    </div>
                    <div style="margin-top:10px; border-top:1px solid #334155; padding-top:8px; font-size:11px;">
                        <b>Required Bill of Materials (BoM):</b>
                        <div style="color:#94A3B8; font-size:11px; margin-top:4px;">
                """,
                unsafe_allow_html=True,
            )
            for item in sap_data.get("bill_of_materials", []):
                st.markdown(
                    f"<div style='margin-left:8px; color:#CBD5E1;'>• <code>{item['part_no']}</code>: {item['description']} (Qty: {item['qty']} {item['unit']})</div>",
                    unsafe_allow_html=True,
                )
            st.markdown(
                """
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c_btn1, c_btn2 = st.columns(2)
            if c_btn1.button("Dispatch Work Order to CMMS", use_container_width=True, type="primary"):
                st.success(f"Work order {sap_data['work_order_id']} dispatched to {sap_data['work_center']}.")
            if c_btn2.button("Print Maintenance Order", use_container_width=True):
                st.info("Maintenance order sheet queued for export.")

        with col_sop:
            st.markdown("#### Standard Operating Procedure (SOP) Action Steps")
            action_steps = sap_data.get("action_steps", snap.get("immediate_actions", []))
            for act in action_steps:
                st.markdown(
                    f"""
                    <div class="action-item">
                        <b>Step {act.get('step', 1)}:</b> {act.get('action', '')}
                        <div style="font-size:10px; color:#94A3B8; margin-top:3px;">
                            Timeframe: {act.get('timeframe', '< 30 min')} &nbsp;|&nbsp; Source: <b>{act.get('source', 'RCA-2')}</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
            st.markdown("#### Corrective & Preventive Actions (CAPA) Log")
            for capa in snap["permanent_capa"][:3]:
                st.markdown(
                    f"""
                    <div class="capa-item">
                        <b>{capa.get('category', 'Technical CAPA')}:</b> {capa.get('action', '')}
                        <div style="font-size:10px; color:#94A3B8; margin-top:3px;">
                            PIC: <b>{capa.get('pic', 'Reliability')}</b> &nbsp;|&nbsp; Target: <b>{capa.get('due_date', '2026-05-30')}</b> &nbsp;|&nbsp; Ref: {capa.get('source', 'RCA-2')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # =========================================================================
    # TAB 4: PLANT ASSETS & FAILURE ANALYSIS
    # =========================================================================
    with tab4:
        st.markdown("### Adaptive Shutdown Cost & Delay Calculator (P-F Degradation)")
        st.caption("3-state physical machine model evaluating the cost of delay against projected downtime (8h vs 32h) and financial loss:")

        # 3-State Physical Machine Adaptation
        if current_hour < 633:
            preview_failure = st.toggle(
                "Preview Failure Scenario (Hours 633-679)",
                value=False,
                help="Inspect the theoretical degradation curve without violating physical timeline consistency",
            )
            if not preview_failure:
                st.markdown(
                    """
                    <div style="background:#1E293B; border:1px solid #10B981; border-radius:6px; padding:14px 18px; margin-bottom:14px;">
                        <div style="font-size:13px; font-weight:700; color:#10B981; text-transform:uppercase;">
                            State 1: Normal Steady Operation (Hours 0 - 632)
                        </div>
                        <div style="font-size:12px; color:#F8FAFC; margin-top:4px;">
                            Point P has not been reached. The machine is operating reliably within design limits at 55.0 T/H capacity. No turnaround or shutdown intervention is required.
                        </div>
                        <div class="grid-kpi-static">
                            <div class="kpi-box-static">
                                <div class="cbm-label">Projected Downtime</div>
                                <div class="cbm-val" style="color:#10B981;">0.0 Hours</div>
                                <div class="cbm-sub">Full Production</div>
                            </div>
                            <div class="kpi-box-static">
                                <div class="cbm-label">Turnaround Loss</div>
                                <div class="cbm-val" style="color:#10B981;">$0.0k</div>
                                <div class="cbm-sub">@ 55.0 T/H Load</div>
                            </div>
                            <div class="kpi-box-static">
                                <div class="cbm-label">Cost of Delay</div>
                                <div class="cbm-val" style="color:#94A3B8;">$0.0k</div>
                                <div class="cbm-sub">No Inaction Penalty</div>
                            </div>
                            <div class="kpi-box-static">
                                <div class="cbm-label">Point P Status</div>
                                <div class="cbm-val" style="color:#38BDF8;">Not Reached</div>
                                <div class="cbm-sub">Normal Steady Envelope</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                # Render interactive HTML P-F slider
                components.html(
                    """
                    <!DOCTYPE html>
                    <html>
                    <head>
                    <style>
                    body {
                        margin: 0; padding: 0; background-color: transparent;
                        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        color: #F8FAFC;
                    }
                    .sim-container {
                        background-color: #1E293B; border: 1px solid #334155; border-radius: 6px; padding: 16px 20px;
                    }
                    .grid-kpi {
                        display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px;
                    }
                    .kpi-box {
                        background-color: #0F172A; border: 1px solid #334155; border-radius: 4px; padding: 10px 14px;
                    }
                    .kpi-title {
                        font-size: 11px; text-transform: uppercase; color: #94A3B8; font-weight: 600; letter-spacing: 0.5px;
                    }
                    .kpi-value {
                        font-size: 22px; font-weight: 700; color: #F8FAFC; margin-top: 4px; transition: color 0.15s ease;
                    }
                    .kpi-badge {
                        font-size: 11px; color: #38BDF8; margin-top: 2px;
                    }
                    .slider-row {
                        display: flex; flex-direction: column; gap: 6px;
                    }
                    .slider-labels {
                        display: flex; justify-content: space-between; font-size: 11px; color: #94A3B8; font-family: monospace;
                    }
                    input[type=range] {
                        -webkit-appearance: none; width: 100%; background: #334155; height: 8px; border-radius: 4px; outline: none; cursor: pointer;
                    }
                    input[type=range]::-webkit-slider-thumb {
                        -webkit-appearance: none; appearance: none; width: 20px; height: 20px; border-radius: 50%;
                        background: #38BDF8; cursor: pointer; border: 2px solid #F8FAFC; box-shadow: 0 0 6px rgba(56, 189, 248, 0.5);
                    }
                    </style>
                    </head>
                    <body>
                    <div class="sim-container">
                        <div class="grid-kpi">
                            <div class="kpi-box">
                                <div class="kpi-title">Intervention Hour</div>
                                <div id="hr-val" class="kpi-value" style="color:#38BDF8;">Hr 633</div>
                                <div id="delay-val" class="kpi-badge">+0h Delay</div>
                            </div>
                            <div class="kpi-box">
                                <div class="kpi-title">Projected Turnaround</div>
                                <div id="dt-val" class="kpi-value" style="color:#F59E0B;">8.0 Hours</div>
                                <div class="kpi-badge">vs 32h Unplanned Trip</div>
                            </div>
                            <div class="kpi-box">
                                <div class="kpi-title">Cost of Delay</div>
                                <div id="cost-val" class="kpi-value" style="color:#EF4444;">$0.0k</div>
                                <div class="kpi-badge">@ $49.5k/hr downtime</div>
                            </div>
                            <div class="kpi-box">
                                <div class="kpi-title">Net Cost Savings</div>
                                <div id="save-val" class="kpi-value" style="color:#10B981;">$1,188.0k USD</div>
                                <div class="kpi-badge">vs $1,584.0k Total Loss</div>
                            </div>
                        </div>
                        <div class="slider-row">
                            <div class="slider-labels">
                                <span>Point P: Hr 633 (Immediate 8h Turnaround)</span>
                                <span id="slider-curr" style="color:#38BDF8; font-weight:700;">Selected Action Hour: 633</span>
                                <span>Point F: Hr 679 (Unplanned 32h Trip)</span>
                            </div>
                            <input type="range" id="t-slider" min="633" max="679" value="633" oninput="updateSim(this.value)">
                        </div>
                    </div>
                    <script>
                    function updateSim(val) {
                        val = parseInt(val);
                        let elapsed = val - 633;
                        let dt = 8.0 + 24.0 * Math.pow(elapsed / 46.0, 2);
                        let delayCost = (dt - 8.0) * 49.5;
                        let savings = Math.max(0, (32.0 - dt) * 49.5);
                        document.getElementById('slider-curr').innerText = 'Selected Action Hour: ' + val;
                        document.getElementById('hr-val').innerText = 'Hr ' + val;
                        document.getElementById('delay-val').innerText = '+' + elapsed + 'h Delay';
                        document.getElementById('dt-val').innerText = dt.toFixed(1) + ' Hours';
                        document.getElementById('cost-val').innerText = '$' + delayCost.toFixed(1) + 'k';
                        document.getElementById('save-val').innerText = '$' + savings.toLocaleString('en-US', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + 'k USD';
                    }
                    </script>
                    </body>
                    </html>
                    """,
                    height=165,
                )
                st.plotly_chart(create_pf_escalation_chart(633), use_container_width=True)

        elif 633 <= current_hour < 679:
            # State 2: Active P-F Window
            sim = provider.simulate_pf_decision(current_hour)
            st.markdown(
                f"""
                <div style="background:#1E293B; border:1px solid #F59E0B; border-radius:6px; padding:14px 18px; margin-bottom:14px;">
                    <div style="font-size:13px; font-weight:700; color:#F59E0B; text-transform:uppercase;">
                        State 2: Active P-F Degradation Window (Hour {current_hour})
                    </div>
                    <div style="font-size:12px; color:#F8FAFC; margin-top:4px;">
                        Point P detected at Hour 633. Delaying controlled intervention increases turnaround duration from 8.0 hours up to 32.0 hours.
                    </div>
                    <div class="grid-kpi-static">
                        <div class="kpi-box-static">
                            <div class="cbm-label">Intervention Hour</div>
                            <div class="cbm-val" style="color:#38BDF8;">Hr {current_hour}</div>
                            <div class="cbm-sub">+{current_hour - 633}h Delay Elapsed</div>
                        </div>
                        <div class="kpi-box-static">
                            <div class="cbm-label">Projected Turnaround</div>
                            <div class="cbm-val" style="color:#F59E0B;">{sim['projected_downtime_hrs']:.1f} Hours</div>
                            <div class="cbm-sub">vs 32h Unplanned Trip</div>
                        </div>
                        <div class="kpi-box-static">
                            <div class="cbm-label">Cost of Delay</div>
                            <div class="cbm-val" style="color:#EF4444;">${sim['cost_of_delay_k_usd']:.1f}k</div>
                            <div class="cbm-sub">@ $49.5k/hr Downtime</div>
                        </div>
                        <div class="kpi-box-static">
                            <div class="cbm-label">Net Cost Savings</div>
                            <div class="cbm-val" style="color:#10B981;">${sim['net_savings_k_usd']:,.1f}k USD</div>
                            <div class="cbm-sub">vs $1,584.0k Total Loss</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.plotly_chart(create_pf_escalation_chart(current_hour), use_container_width=True)

        else:
            # State 3: Post-Trip Emergency Stoppage (Hours 679+)
            st.markdown(
                """
                <div style="background:#1E293B; border:1px solid #EF4444; border-radius:6px; padding:14px 18px; margin-bottom:14px;">
                    <div style="font-size:13px; font-weight:700; color:#EF4444; text-transform:uppercase;">
                        State 3: Post-Trip Emergency Stoppage (Hours 679+)
                    </div>
                    <div style="font-size:12px; color:#F8FAFC; margin-top:4px;">
                        Point F reached. Machine trip occurred (RUN_STATUS = 0). The 16-hour proactive intervention window has expired.
                    </div>
                    <div class="grid-kpi-static">
                        <div class="kpi-box-static">
                            <div class="cbm-label">Actual Downtime</div>
                            <div class="cbm-val" style="color:#EF4444;">32.0 Hours</div>
                            <div class="cbm-sub">Emergency Outage</div>
                        </div>
                        <div class="kpi-box-static">
                            <div class="cbm-label">Actual Turnaround Loss</div>
                            <div class="cbm-val" style="color:#EF4444;">$1,584.0k</div>
                            <div class="cbm-sub">$1.584M USD Impact</div>
                        </div>
                        <div class="kpi-box-static">
                            <div class="cbm-label">Cost of Delay</div>
                            <div class="cbm-val" style="color:#EF4444;">$1,188.0k</div>
                            <div class="cbm-sub">Inaction Escalation</div>
                        </div>
                        <div class="kpi-box-static">
                            <div class="cbm-label">Net Savings</div>
                            <div class="cbm-val" style="color:#94A3B8;">$0.0k USD</div>
                            <div class="cbm-sub">Window Expired</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.plotly_chart(create_pf_escalation_chart(679), use_container_width=True)

        with st.expander("Turnaround Downtime Escalation Protocol Justification (ISO 14224 / API 581)"):
            st.markdown(
                """
                - **Planned Controlled Shutdown Baseline (8 Hours) [ENGINEERING ASSUMPTION]:**
                  - 2 Hours: Controlled furnace rate ramp-down, train depressurization, and compressor cooling.
                  - 4 Hours: Babbitt insert journal bearing replacement and lube-oil flushing with clean synthetic ISO VG 46 lubricant.
                  - 2 Hours: Gradual machine spin-up, heat synchronization, and ramp back to full 55.0 T/H cracking capacity.
                - **Unplanned Machine Trip Baseline (32 Hours) [FACT - RCA-2 / AR-2026-ZCU-0142]:**
                  - Catastrophic rotor contact and bearing wipe-out required extensive casing disassembly, shaft realignment, and emergency turnaround.
                """
            )

        st.markdown("---")

        # Enterprise Portfolio Risk Overview
        st.markdown("### Plant ZCU Portfolio Risk & Fleet Criticality Overview")
        fc1, fc2, fc3, fc4 = st.columns(4)
        fc1.metric("Plant ZCU Portfolio Risk", f"${fleet_meta['zcu_portfolio_risk_k_usd']/1000.0:.2f}M USD", f"{fleet_meta['zcu_incident_count']} Incidents (Rank #1)")
        fc2.metric("12-Plant Complex Exposure", f"${fleet_meta['complex_total_exposure_k_usd']/1000.0:.2f}M USD", f"{fleet_meta['complex_incident_count']} Total Incidents")
        fc3.metric("Monitored ZCU Assets", f"{fleet_meta['total_assets']} Equipment", "17 Rotary | 10 Elec | 29 Static")
        fc4.metric("Data Provenance Ratio", "2 FACT : 54 HYPOTHESIS", "Official RCAs vs FMEA Engineering")

        st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)

        # Interactive Fleet Filters
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

        # Display Fleet Table
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
        st.caption(f"Displaying {len(table_df)} of {fleet_meta['total_assets']} Plant ZCU assets.")


if __name__ == "__main__":
    main()
