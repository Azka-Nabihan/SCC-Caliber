"""
Chandra Asri Petrochemical — Plant ZCU Predictive Reliability & Condition Monitoring System.
Single Pane of Glass (SPOG) Condition-Based Maintenance (CBM) Console for CALIBER 2026.
Complies with ISA-18.2 Alarm Management, ISA-5.1 Tagging, ISO 10816-3 Vibration Limits, and API 581 Risk Modeling.
"""

import streamlit as st
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

# Page Configuration (100% Industrial English UI, Clean Standards)
st.set_page_config(
    page_title="Chandra Asri Plant ZCU Condition Monitoring | CALIBER 2026",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Industrial CSS Styling (Flat DCS Slate Theme, Zero Glow/Emojis)
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

    # --- SIDEBAR OPERATOR CONSOLE ---
    st.sidebar.markdown("### Operator Control Console")

    # Pilot Asset Selector
    asset_selection = st.sidebar.selectbox(
        "Monitored Asset",
        options=["KO-3201 (Cracked Gas Compressor - ZCU)"],
        index=0,
        help="Pilot Asset MVP with 720h verified continuous telemetry. 56 Plant ZCU fleet assets available in Tab 3.",
    )
    st.sidebar.caption("Pilot Asset MVP (56 ZCU Fleet Assets indexed in Tab 3)")

    # Operational Timeline Bookmarks
    st.sidebar.markdown("#### Operational Bookmarks")
    c_bm1, c_bm2 = st.sidebar.columns(2)
    c_bm3, c_bm4 = st.sidebar.columns(2)

    if "timeline_slider" not in st.session_state:
        st.session_state.timeline_slider = 633

    if c_bm1.button("Hr 100: Normal Steady", use_container_width=True, help="Baseline steady-state operation"):
        st.session_state.timeline_slider = 100
        st.rerun()
    if c_bm2.button("Hr 633: GDN Alert", use_container_width=True, help="Early Warning: 16h before DCS alarm"):
        st.session_state.timeline_slider = 633
        st.rerun()
    if c_bm3.button("Hr 649: DCS Alarm", use_container_width=True, help="Conventional 45 um alarm threshold reached"):
        st.session_state.timeline_slider = 649
        st.rerun()
    if c_bm4.button("Hr 679: Trip Post", use_container_width=True, help="Actual machine trip (RUN_STATUS=0)"):
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

    # Sidebar Status Indicator
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
    st.sidebar.markdown(f"**Vibration:** `{snap['vibration']:.2f} µm` (Alarm: 45 µm | Trip: 75 µm)")
    st.sidebar.markdown(f"**Health Index:** `{snap['health_index']:.1f}%` (ISO 10816-3)")

    # Optional AI Shift Briefing Generation Checkbox
    st.sidebar.markdown("---")
    enable_gemini = st.sidebar.checkbox(
        "Enable Gemini API Briefing",
        value=False,
        help="Query Google Gemini 1.5 Pro to synthesize natural-language briefing instead of zero-latency deterministic rule engine.",
    )

    st.sidebar.caption("Deterministic Inference Engine: <2 ms lookup")

    # Render Main Header
    render_header()

    # --- 3-TAB APPLICATION STRUCTURE ---
    tab1, tab2, tab3 = st.tabs([
        "Tab 1: Operational Cockpit & Prescriptive Actions",
        "Tab 2: Telemetry Diagnostics & P-F Escalation Analysis",
        "Tab 3: Plant ZCU Fleet Reliability & Asset Criticality Matrix",
    ])

    # =========================================================================
    # TAB 1: OPERATIONAL COCKPIT & PRESCRIPTIVE ACTIONS
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

        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)

        # Row 2: DCS Industrial 60/40 Split Console
        col_left, col_right = st.columns([1.4, 1.0])

        # --- LEFT COLUMN (60%): TELEMETRY LEAD TIME & HANDOVER LOG ---
        with col_left:
            st.markdown("#### Shaft Vibration Trend vs DCS Alarm Thresholds")
            st.plotly_chart(create_compact_vibration_trend(df, current_hour), use_container_width=True)

            # Automated Shift Supervisor Handover Note
            st.markdown("#### Shift Supervisor Handover Note")
            if enable_gemini:
                with st.spinner("Synthesizing Shift Handover Note via Gemini 1.5 Pro API..."):
                    llm_card = provider.recommender.generate_action_card(
                        tag_number="KO-3201",
                        anomaly_info=snap,
                        use_llm=True,
                    )
                    active_note = llm_card["copilot_shift_briefing"]
                    active_mode = llm_card["synthesis_mode"]
            else:
                active_note = snap["copilot_shift_briefing"]
                active_mode = snap["synthesis_mode"]

            st.markdown(
                f"""
                <div style="background:#1E293B; border:1px solid #334155; border-left:3px solid #38BDF8; border-radius:4px; padding:12px 16px; font-size:13px; line-height:1.5;">
                    <div style="font-weight:600; color:#38BDF8; font-size:11px; text-transform:uppercase; margin-bottom:4px;">
                        Technical Summary (Shift Handover Log)
                    </div>
                    {active_note}
                    <div style="font-size:10px; color:#64748B; margin-top:8px;">
                        Provenance: <code>{active_mode}</code> &nbsp;|&nbsp; Asset Tag: <b>KO-3201</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # --- RIGHT COLUMN (40%): PRESCRIPTIVE ACTIONS & RISK CONSOLE ---
        with col_right:
            st.markdown("#### Standard Operating Procedure (SOP) Action Plan (< 30 Mins)")
            for act in snap["immediate_actions"]:
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

            st.markdown("#### Historical Failure Reference (Similar Incidents)")
            similar_incs = provider.get_similar_incidents(equipment_type="COMPRESSOR", top_k=2)
            sim_df = pd.DataFrame(similar_incs).rename(columns={
                "incident_reference": "Incident No",
                "tag_number": "Tag",
                "actual_downtime_hrs": "Downtime (h)",
                "actual_loss_k_usd": "Loss ($k)",
            })
            st.dataframe(
                sim_df[["Incident No", "Tag", "Downtime (h)", "Loss ($k)"]],
                use_container_width=True,
                hide_index=True,
            )

    # =========================================================================
    # TAB 2: TELEMETRY DIAGNOSTICS & P-F ESCALATION ANALYSIS
    # =========================================================================
    with tab2:
        st.markdown("### Process Instrumentation Telemetry & Anomaly Attribution")
        st.caption("Continuous 720-hour OSIsoft PI telemetry streams synchronized with Graph Deviation Network (GDN) multimodal anomaly scores:")

        # Detailed two-tier telemetry chart
        st.plotly_chart(create_telemetry_trend_chart(df, current_hour), use_container_width=True)

        st.markdown(
            """
            <div style="background:#1E293B; border:1px solid #334155; border-left:3px solid #818CF8; padding:10px 14px; border-radius:4px; font-size:12px; margin-bottom:14px;">
                <b>Engineering Diagnostic Note (Hour 633):</b> Upstream process conditions (<i>Plant Rate: 56.3 T/H, Feed Flow: 55.4 T/H, Bearing Temp: 64.5 °C</i>) remain within stable design envelopes. The GDN anomaly score (10.72) is localized to shaft radial vibration micro-deviation, confirming early babbitt bearing distress rather than process instability.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Process Mimic Flow Strip (ISA-5.1)
        st.markdown("### Plant ZCU Process Mimic & Sensor Loop Mapping (ISA-5.1)")
        st.plotly_chart(
            create_process_mimic_chart(
                snap["top_contributors"],
                current_hour,
                snap["vibration"],
            ),
            use_container_width=True,
        )

        st.markdown("---")

        # P-F Curve Decision Escalation Simulator
        st.markdown("### Turnaround Decision Escalation Simulator (P-F Curve)")
        st.caption("What-If turnaround delay analysis from initial anomaly detection (Hour 633) to machine trip (Hour 679):")

        sim_hour = st.slider(
            "Controlled Turnaround Decision Hour (t_action)",
            min_value=633,
            max_value=679,
            value=max(633, min(679, current_hour)),
            key="sim_action_hour",
        )

        # Economic KPI calculation
        delta_t = 46.0
        elapsed = sim_hour - 633
        proj_downtime = 8.0 + 24.0 * ((elapsed / delta_t) ** 2)
        cost_delay = (proj_downtime - 8.0) * 55.0 * 900.0 / 1000.0
        net_saved = max(0.0, (32.0 - proj_downtime) * 55.0 * 900.0 / 1000.0)

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Intervention Hour", f"Hr {sim_hour}", f"+{elapsed}h Delay")
        s2.metric("Projected Turnaround", f"{proj_downtime:.1f} Hours", "vs 32h Unplanned Trip")
        s3.metric("Cost of Delay", f"${cost_delay:,.1f}k", "@ $49.5k/hr downtime")
        s4.metric("Net Cost Savings", f"${net_saved:,.1f}k USD", "vs $1,584.0k Total Loss")

        st.plotly_chart(create_pf_escalation_chart(sim_hour), use_container_width=True)

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

    # =========================================================================
    # TAB 3: PLANT ZCU FLEET RELIABILITY & ASSET CRITICALITY MATRIX
    # =========================================================================
    with tab3:
        st.markdown("### Plant ZCU Fleet Reliability & Asset Criticality Matrix")
        st.caption("Fleet health, failure modes, and risk exposure across all 56 Plant ZCU equipments:")

        fleet_meta = provider.get_fleet_matrix()

        # Enterprise Exposure Metrics
        fc1, fc2, fc3, fc4 = st.columns(4)
        fc1.metric("Plant ZCU Portfolio Risk", f"${fleet_meta['zcu_portfolio_risk_k_usd']/1000.0:.2f}M USD", f"{fleet_meta['zcu_incident_count']} Incidents (Rank #1)")
        fc2.metric("12-Plant Complex Exposure", f"${fleet_meta['complex_total_exposure_k_usd']/1000.0:.2f}M USD", f"{fleet_meta['complex_incident_count']} Total Incidents")
        fc3.metric("Monitored ZCU Assets", f"{fleet_meta['total_assets']} Equipment", "17 Rotary | 10 Elec | 29 Static")
        fc4.metric("Data Provenance Ratio", "2 FACT : 54 HYPOTHESIS", "Official RCAs vs FMEA Engineering")

        st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

        # Interactive Filters
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
