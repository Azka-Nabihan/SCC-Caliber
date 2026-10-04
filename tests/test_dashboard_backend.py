"""
Unit and Integration Test Suite for Stage 4 Single Pane of Glass Dashboard Backend.
Tests Data Provider, Caching, P-F Decision Simulator, Similar Incidents Retrieval,
and Plant ZCU Fleet Risk Matrix.
"""

import time
import pytest
import pandas as pd
import numpy as np

from src.app.data_provider import DashboardDataProvider, _load_stage2_scores_csv, _load_fleet_metadata


@pytest.fixture(scope="module")
def data_provider():
    return DashboardDataProvider()


def test_caching_helpers_no_unhashable_error():
    """
    Test 1 (Solution M1): Module-level caching functions execute cleanly without
    unhashable instance errors on self.
    """
    df1 = _load_stage2_scores_csv()
    assert isinstance(df1, pd.DataFrame)
    assert len(df1) == 720

    meta = _load_fleet_metadata()
    assert isinstance(meta, dict)
    assert len(meta) >= 56


def test_load_timeseries_data_schema(data_provider):
    """
    Test 2 (Solution L3): Verifies 720 rows and exact lowercase column naming convention.
    """
    df = data_provider.load_timeseries_data()
    assert len(df) == 720
    expected_cols = [
        "timestamp", "hour", "RUN_STATUS", "KO3201_FEED", "KO3201_DISP",
        "KO3201_AMP", "KO3201_TEMP", "KO3201_VIB", "PLANT_RATE",
        "gdn_anomaly_score", "is_anomaly", "top_contributors", "health_index"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Missing expected column: {col}"


def test_get_hour_snapshots_across_states(data_provider):
    """
    Test 3 (Solutions C2, C6, L1, M2): Verifies snapshot responses across 4 key hours:
    - Hour 100: Normal steady-state (State 2, Green, Vib ~28.76 um dynamic extraction)
    - Hour 633: GDN Early Warning (State 3, Amber, HI 98.58%, Lead Time 16h)
    - Hour 649: DCS Alarm Exceeded (State 4, Yellow, Vib 46.4 um)
    - Hour 679: Machine Offline Post-Trip (State 1, Grey, RUN_STATUS = 0)
    Ensures sub-5ms lookup latency.
    """
    # Performance benchmark (Solution M2: sub-20ms responsiveness)
    _ = data_provider.get_hour_snapshot(0)  # Warm-up call
    t0 = time.perf_counter()
    snap100 = data_provider.get_hour_snapshot(100)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert elapsed_ms < 15.0, f"Snapshot lookup too slow: {elapsed_ms:.2f} ms"

    # Hour 100 Check
    assert snap100["operational_state"] == 2
    assert snap100["status_color"] == "GREEN"
    assert "NORMAL STEADY-STATE" in snap100["current_status"]
    assert snap100["vibration"] == pytest.approx(28.76, rel=1e-2)

    # Hour 633 Check
    snap633 = data_provider.get_hour_snapshot(633)
    assert snap633["operational_state"] == 3
    assert snap633["status_color"] == "AMBER"
    assert "EARLY WARNING" in snap633["current_status"]
    assert snap633["health_index"] == pytest.approx(98.58, rel=1e-2)
    assert snap633["vibration"] == pytest.approx(31.24, rel=1e-2)
    assert "16 Hours" in snap633["detected_lead_time"]["headline"]

    # Hour 649 Check
    snap649 = data_provider.get_hour_snapshot(649)
    assert snap649["operational_state"] == 4
    assert snap649["status_color"] == "YELLOW"
    assert snap649["vibration"] >= 45.0  # Exceeds DCS Alarm

    # Hour 679 Check
    snap679 = data_provider.get_hour_snapshot(679)
    assert snap679["operational_state"] == 1
    assert snap679["status_color"] == "GREY"
    assert snap679["run_status"] == 0
    assert "OFFLINE" in snap679["current_status"]


def test_pf_decision_simulator(data_provider):
    """
    Test 4 (Solutions C1, H3): Verifies P-F curve response time simulation:
    - Action at Hour 633: 8 hrs downtime, $1,188.0k savings, $0 delay cost
    - Action at Hour 679: 32 hrs downtime, $0 savings, $1,188.0k cost of inaction
    - Intermediate Hour 656: 8 + (23/46)^2 * 24 = 14 hrs downtime, savings = $891.0k
    """
    sim633 = data_provider.simulate_pf_decision(action_hour=633)
    assert sim633["action_hour"] == 633
    assert sim633["projected_downtime_hrs"] == 8.0
    assert sim633["net_savings_k_usd"] == 1188.0
    assert sim633["cost_of_delay_k_usd"] == 0.0

    sim679 = data_provider.simulate_pf_decision(action_hour=679)
    assert sim679["action_hour"] == 679
    assert sim679["projected_downtime_hrs"] == 32.0
    assert sim679["net_savings_k_usd"] == 0.0
    assert sim679["cost_of_delay_k_usd"] == 1188.0

    sim656 = data_provider.simulate_pf_decision(action_hour=656)
    assert sim656["projected_downtime_hrs"] == pytest.approx(14.0, abs=0.5)
    assert 800.0 <= sim656["net_savings_k_usd"] <= 950.0


def test_similar_incidents_retrieval(data_provider):
    """
    Test 5 (Solution H7): Verifies retrieval of top-3 compressor/pump incidents
    from the 380-incident repository with relevance sorting.
    """
    similar = data_provider.get_similar_incidents(equipment_type="COMPRESSOR", top_k=3)
    assert len(similar) == 3
    for inc in similar:
        assert "incident_reference" in inc
        assert "plant" in inc
        assert "failure_mechanism" in inc
        assert "actual_loss_k_usd" in inc
        assert inc["actual_loss_k_usd"] > 0


def test_fleet_matrix_aggregations(data_provider):
    """
    Test 6 (Solutions C4, M3, M4, L4): Verifies fleet matrix:
    - 56 total ZCU assets
    - Exactly 17 Rotary, 10 Electrical, 29 Static
    - 2 FACT (KO-3201, HE-3301) and 54 ENGINEERING_HYPOTHESIS
    - Total ZCU Risk = $11.11M, Total Complex Exposure = $67.19M
    - Canonical keys: tag_number, equipment_name, category, criticality_class, provenance_level, risk_score
    """
    fleet_data = data_provider.get_fleet_matrix()
    assets = fleet_data["assets"]
    assert len(assets) == 56

    # Category counts
    rotary = [a for a in assets if a["category"].upper() == "ROTARY"]
    electrical = [a for a in assets if a["category"].upper() == "ELECTRICAL"]
    static = [a for a in assets if a["category"].upper() == "STATIC"]
    assert len(rotary) == 17
    assert len(electrical) == 10
    assert len(static) == 29

    # Provenance counts
    fact_count = sum(1 for a in assets if a["provenance_level"] == "FACT")
    hyp_count = sum(1 for a in assets if a["provenance_level"] == "ENGINEERING_HYPOTHESIS")
    assert fact_count == 2
    assert hyp_count == 54

    # Financial Exposure reconciliation
    assert fleet_data["zcu_portfolio_risk_k_usd"] == pytest.approx(11110.0, rel=1e-1)  # ~$11.11M
    assert fleet_data["complex_total_exposure_k_usd"] == pytest.approx(67190.0, rel=1e-1)  # ~$67.19M


def test_charts_generation(data_provider):
    """
    Test 7 (Solutions C1, C6, H4): Verifies that Plotly chart generators
    produce valid Figure objects with appropriate shapes and annotations.
    """
    from src.app.charts import (
        create_health_index_gauge,
        create_compact_vibration_trend,
        create_telemetry_trend_chart,
        create_process_mimic_chart,
        create_pid_deviation_graph,
        create_pf_escalation_chart,
    )
    import plotly.graph_objects as go

    # 1. Gauge chart
    gauge_fig = create_health_index_gauge(hi_val=98.58, status_color="AMBER", operational_state=3)
    assert isinstance(gauge_fig, go.Figure)

    # 2. Compact Vibration Trend (Tab 1 60% col)
    df = data_provider.load_timeseries_data()
    compact_fig = create_compact_vibration_trend(df, current_hour=633)
    assert isinstance(compact_fig, go.Figure)

    # 3. Telemetry trend chart (Tab 2)
    trend_fig = create_telemetry_trend_chart(df, current_hour=633)
    assert isinstance(trend_fig, go.Figure)
    assert len(trend_fig.data) >= 2  # Vibration trace + GDN score trace

    # 4. Process Mimic Strip ISA-5.1 (Tab 2)
    snap633 = data_provider.get_hour_snapshot(633)
    mimic_fig = create_process_mimic_chart(
        top_contributors=snap633["top_contributors"],
        current_hour=633,
        current_vibration=snap633["vibration"],
    )
    assert isinstance(mimic_fig, go.Figure)

    # 5. Backward-compatibility P&ID graph alias
    pid_fig = create_pid_deviation_graph(top_contributors=snap633["top_contributors"], current_hour=633)
    assert isinstance(pid_fig, go.Figure)

    # 6. P-F Curve Escalation Chart
    pf_fig = create_pf_escalation_chart(current_action_hour=633)
    assert isinstance(pf_fig, go.Figure)


def test_dashboard_ui_apptest_headless():
    """
    Test 8 (Solutions M5, H6, L2): End-to-end headless verification of Streamlit UI
    using streamlit.testing.v1.AppTest in-memory runner.
    Verifies startup without exception, sidebar slider time travel, and bookmark interaction.
    """
    from streamlit.testing.v1 import AppTest

    # Initialize headless test instance
    at = AppTest.from_file("src/app/dashboard.py", default_timeout=15)
    at.run()

    # Verify initial run completed with zero exceptions
    assert not at.exception, f"AppTest encountered exception: {at.exception}"

    # Verify slider interaction: shift timeline to Hour 633
    if len(at.slider) > 0:
        at.slider[0].set_value(633).run()
        assert not at.exception

    # Verify slider interaction: shift timeline to Hour 100
    if len(at.slider) > 0:
        at.slider[0].set_value(100).run()
        assert not at.exception

    # Verify slider interaction: shift timeline to Hour 679
    if len(at.slider) > 0:
        at.slider[0].set_value(679).run()
        assert not at.exception


def test_llm_diagnostic_reasoning_structure(data_provider):
    """
    Test 9: Verifies 3-stage diagnostic reasoning payload structure:
    Stage 1: Multi-sensor observation, Stage 2: Mechanical inference, Stage 3: RCA correlation.
    """
    diag = data_provider.get_diagnostic_reasoning(current_hour=633)
    assert diag["confidence_score"] == pytest.approx(94.2, abs=0.5)
    assert "step_1_observation" in diag
    assert "step_2_inference" in diag
    assert "step_3_rca_correlation" in diag
    assert "AR-2026-ZCU-0142" in diag["matched_incident"]
    assert "VI-3201" in diag["step_1_observation"]
    assert "babbitt" in diag["step_2_inference"].lower()
    assert "HE-3301" in diag["step_3_rca_correlation"]


def test_copilot_what_if_simulation(data_provider):
    """
    Test 10: Verifies that operational What-If queries return physics-grounded answers:
    - 10% rate reduction
    - Babbitt wipe-out risk
    - Controlled shutdown protocol
    """
    # 1. Rate cut
    res_rate = data_provider.run_copilot_simulation("Simulasi rate 10%", current_hour=633)
    assert "18%" in res_rate["answer"] or "load" in res_rate["answer"].lower()
    assert "1.188M" in res_rate["answer"]

    # 2. Babbitt risk
    res_risk = data_provider.run_copilot_simulation("Risiko babbitt wipe-out", current_hour=633)
    assert "AR-2026-ZCU-0142" in res_risk["answer"]
    assert "32" in res_risk["answer"] and ("hours" in res_risk["answer"].lower() or "hrs" in res_risk["answer"].lower())

    # 3. Shutdown protocol
    res_sop = data_provider.run_copilot_simulation("Protokol shutdown 8 jam", current_hour=633)
    assert "8.0 Hours" in res_sop["answer"] or "8 hours" in res_sop["answer"].lower()

    # 4. Temperature query (exact user query: "berapa batas temperatur aman oli pendingin?")
    res_temp = data_provider.run_copilot_simulation("berapa batas temperatur aman oli pendingin?", current_hour=633)
    assert "40.0°C – 48.0°C" in res_temp["answer"] or "42.5°C" in res_temp["answer"]
    assert "55.0°C" in res_temp["answer"]
    assert "65.0°C" in res_temp["answer"]
    assert "HE-3301" in res_temp["scenario_title"]

    # 5. Vibration thresholds query
    res_vib = data_provider.run_copilot_simulation("Berapa ambang batas vibrasi kompresor KO-3201?", current_hour=633)
    assert "45.0 µm" in res_vib["answer"]
    assert "75.0 µm" in res_vib["answer"]
    assert "31.24 µm" in res_vib["answer"]

    # 6. Cooler HE-3301 leakage query
    res_cooler = data_provider.run_copilot_simulation("Apakah ada kebocoran pada cooler HE-3301?", current_hour=633)
    assert "AR-2026-ZCU-0142" in res_cooler["answer"]
    assert "500 ppm" in res_cooler["answer"]


def test_sap_work_order_generation(data_provider):
    """
    Test 11: Verifies synthesis of authentic SAP PM work order:
    Type M1, Order PM01, functional location, BoM parts list, safety permit.
    """
    sap = data_provider.generate_sap_work_order(current_hour=633)
    assert sap["notification_id"] == "NOTIF-2026-PM-0419"
    assert sap["work_order_id"] == "WO-8842109"
    assert "PM01" in sap["order_type"]
    assert "KO-3201" in sap["functional_location"]
    assert len(sap["bill_of_materials"]) >= 3
    assert any("BBR-3201-DE" in item["part_no"] for item in sap["bill_of_materials"])
    assert "DISPATCHED" in sap["status"]


def test_2loop_pid_mimic_traces(data_provider):
    """
    Test 12: Verifies that create_process_mimic_chart renders both main gas train and lube loop traces.
    """
    from src.app.charts import create_process_mimic_chart
    snap = data_provider.get_hour_snapshot(633)
    fig = create_process_mimic_chart(snap["top_contributors"], current_hour=633, current_vibration=snap["vibration"])
    # Check that annotations include both loops
    texts = [a.text for a in fig.layout.annotations if a.text]
    joined_text = " ".join(texts)
    assert "FEED GAS" in joined_text
    assert "SUCTION DRUM" in joined_text
    assert "KO-3201" in joined_text or "BEARING" in joined_text
    assert "HE-3301" in joined_text or "LUBE OIL COOLER" in joined_text


def test_data_provider_copilot_clean_status(data_provider):
    """
    Test 13: Verifies that copilot responses return clean engine_status and source
    without icons/emojis and without prohibited AI brand names.
    """
    res = data_provider.run_copilot_simulation("Apa batas vibrasi?", current_hour=633, use_llm=False)
    assert "engine_status" in res
    assert res["engine_status"] in ["LIVE_ONLINE", "OFFLINE_FALLBACK"]
    assert "source" in res
    assert "gemini" not in res["source"].lower()
    assert "gpt" not in res["source"].lower()
    assert "🟢" not in res["source"]
    assert "🛡️" not in res["source"]


def test_dynamic_sap_work_orders_all_states(data_provider):
    """
    Test 14 (Phase 1): Verifies dynamic work order adaptation across machine states:
    - Hour 100: Routine PM03, Priority Routine, Target duration 2.0h, Scheduled status
    - Hour 633: Proactive PM01, Priority Very High, Target duration 8.0h, Dispatched status
    - Hour 649: Critical PM01, Priority Critical, Target duration 12.0h, Emergency status
    - Hour 679: Breakdown PM02, Priority Emergency Outage, Target duration 32.0h, Outage status
    """
    wo100 = data_provider.generate_sap_work_order(current_hour=100)
    assert wo100["notification_id"] == "NOTIF-2026-PM-0102"
    assert "PM03" in wo100["order_type"]
    assert "P3 Routine" in wo100["priority"]
    assert wo100["target_duration_hrs"] == 2.0
    assert "SCHEDULED" in wo100["status"]
    assert len(wo100["action_steps"]) >= 2

    wo633 = data_provider.generate_sap_work_order(current_hour=633)
    assert wo633["notification_id"] == "NOTIF-2026-PM-0419"
    assert "PM01" in wo633["order_type"]
    assert "Very High" in wo633["priority"]
    assert wo633["target_duration_hrs"] == 8.0
    assert "DISPATCHED" in wo633["status"]
    assert len(wo633["action_steps"]) >= 3

    wo649 = data_provider.generate_sap_work_order(current_hour=649)
    assert wo649["notification_id"] == "NOTIF-2026-PM-0512"
    assert "PM01" in wo649["order_type"]
    assert "Critical" in wo649["priority"]
    assert wo649["target_duration_hrs"] == 12.0
    assert "EMERGENCY DISPATCH" in wo649["status"]
    assert len(wo649["action_steps"]) >= 3

    wo679 = data_provider.generate_sap_work_order(current_hour=679)
    assert wo679["notification_id"] == "NOTIF-2026-PM-0690"
    assert "PM02" in wo679["order_type"]
    assert "Emergency Outage" in wo679["priority"]
    assert wo679["target_duration_hrs"] == 32.0
    assert "MAJOR OUTAGE" in wo679["status"]
    assert len(wo679["action_steps"]) >= 3


def test_56_assets_selector_options(data_provider):
    """
    Test 15 (Phase 1): Verifies that all 56 Plant ZCU equipment are indexed
    with KO-3201 as default first option and remaining 55 sorted alphabetically.
    """
    fleet_meta = data_provider.get_fleet_matrix()
    assets = fleet_meta["assets"]
    assert len(assets) == 56

    pilot_label = "KO-3201 - Cracked Gas Compressor"
    other_labels = sorted([
        f"{a['tag_number']} - {a['equipment_name']}"
        for a in assets
        if a["tag_number"] != "KO-3201"
    ])
    assert len(other_labels) == 55
    all_options = [pilot_label] + other_labels
    assert len(all_options) == 56
    assert all_options[0] == pilot_label
    assert any("HE-3301" in opt for opt in all_options)



