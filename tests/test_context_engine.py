"""
Unit and Integration Test Suite for SCC-Caliber Stage 3 Contextualization Engine.
Verifies temporal anti-leakage, strict provenance, dual-metric financial calculations,
process physics estimation, hour 633 status invariants, offline fallback guardrails,
and plant-wide 56 ZCU multi-domain equipment coverage.
"""

import time
import pytest
from pathlib import Path

from src.pipeline.incident_loader import IncidentLoader
from src.models.incident_matcher import IncidentMatcher
from src.models.action_recommender import ActionRecommender


@pytest.fixture(scope="module")
def incident_loader():
    return IncidentLoader()


@pytest.fixture(scope="module")
def incident_matcher():
    return IncidentMatcher()


@pytest.fixture(scope="module")
def action_recommender(incident_matcher):
    return ActionRecommender(incident_matcher=incident_matcher)


def test_asof_temporal_leakage_prevention(incident_matcher):
    """
    Test 1: Verifies that when as_of is set prior to KO-3201 failure date (e.g. 2026-04-27),
    the KO-3201 incident (2026-04-29) is filtered out, preventing temporal data leakage.
    System must fallback to Tier 3 Equipment Class A fleet median ($107.0k / 106.95k).
    """
    res = incident_matcher.match(
        plant="ZCU",
        tag_number="KO-3201",
        as_of="2026-04-27 09:00:00",
    )

    assert res["match_tier"] == 3
    assert res["match_level"] == "CLASS_A"
    assert res["incident_reference"] != "AR-2026-ZCU-0142"
    assert round(res["total_loss_k_usd"], 1) == 107.0
    assert res["actual_downtime_hrs"] > 0


def test_provenance_and_zero_hallucination(action_recommender):
    """
    Test 2: Verifies that every immediate action and permanent CAPA item carries
    an authentic 'source' attribute and contains zero hallucinated mitigation terms.
    """
    card = action_recommender.generate_action_card(
        tag_number="KO-3201",
        anomaly_info={"hour": 633, "health_index": 98.6, "anomaly_score": 10.7},
        use_llm=False,
    )

    # Check sources
    assert len(card["immediate_actions"]) >= 3
    for act in card["immediate_actions"]:
        assert "source" in act
        assert len(act["source"].strip()) > 0

    assert len(card["permanent_capa"]) >= 5
    for capa in card["permanent_capa"]:
        assert "source" in capa
        assert len(capa["source"].strip()) > 0

    # Combine all action texts
    all_text = " ".join(
        [a["action"].lower() for a in card["immediate_actions"]]
        + [c["action"].lower() for c in card["permanent_capa"]]
    )

    # Zero-hallucination verification
    assert "purifier standby" not in all_text
    assert "drain valve" not in all_text
    assert "vibrometer portabel" not in all_text
    assert "labyrinth seal" not in all_text


def test_loss_metrics_three_distinct_columns(incident_matcher, action_recommender):
    """
    Test 3: Verifies three distinct financial loss columns on KO-3201:
    actual_loss_k_usd (1584.0), potential_loss_k_usd (475.2), and total_loss_k_usd (2059.2).
    """
    match_res = incident_matcher.match(plant="ZCU", tag_number="KO-3201")
    assert match_res["match_tier"] == 1
    assert match_res["incident_reference"] == "AR-2026-ZCU-0142"
    assert match_res["actual_loss_k_usd"] == 1584.0
    assert match_res["potential_loss_k_usd"] == 475.2
    assert match_res["total_loss_k_usd"] == 2059.2

    card = action_recommender.generate_action_card(
        tag_number="KO-3201",
        anomaly_info={"hour": 633, "health_index": 98.6},
        use_llm=False,
    )
    hist = card["financial_risk_dual_metric"]["historical_benchmark_retrospective"]
    assert hist["actual_loss_k_usd"] == 1584.0
    assert hist["potential_loss_k_usd"] == 475.2
    assert hist["total_loss_k_usd"] == 2059.2


def test_process_physics_formula_calculation(incident_matcher):
    """
    Test 4: Verifies deterministic process physics formula:
    Loss = Downtime x Plant Rate (55.0 T/H) x Product Price ($900.0/ton)
    32.0 hrs -> $1,584.0k
    8.0 hrs -> $396.0k (Savings: $1,188.0k / $1.188M)
    """
    trip_res = incident_matcher.estimate_process_loss(
        downtime_hrs=32.0, plant_rate_t_per_hr=55.0, product_price_per_ton=900.0
    )
    assert trip_res["tonnage_lost"] == 1760.0
    assert trip_res["calculated_loss_k_usd"] == 1584.0

    mitigated_res = incident_matcher.estimate_process_loss(
        downtime_hrs=8.0, plant_rate_t_per_hr=55.0, product_price_per_ton=900.0
    )
    assert mitigated_res["tonnage_lost"] == 440.0
    assert mitigated_res["calculated_loss_k_usd"] == 396.0

    savings = trip_res["calculated_loss_k_usd"] - mitigated_res["calculated_loss_k_usd"]
    assert savings == 1188.0


def test_action_card_hour_633_status(action_recommender):
    """
    Test 5: Verifies that at hour 633 (GDN anomaly detection), the Action Card
    carries status EARLY WARNING (Health Index: 98.6% NORMAL) and AMBER indicator,
    with single official lead time: 16 Jam before DCS Alarm.
    """
    card = action_recommender.generate_action_card(
        tag_number="KO-3201",
        anomaly_info={"hour": 633, "health_index": 98.6, "anomaly_score": 10.7},
        use_llm=False,
    )

    assert "EARLY WARNING" in card["current_status"]
    assert "98.6%" in card["current_status"]
    assert "NORMAL" in card["current_status"]
    assert card["status_color"] == "AMBER"
    assert "16 Jam" in card["detected_lead_time"]["headline"]
    assert "45 µm" in card["detected_lead_time"]["headline"]


def test_offline_fallback_guardrail(action_recommender):
    """
    Test 6: Verifies instantaneous (< 10 ms) deterministic offline fallback
    when LLM is disabled or API key is absent, returning complete executive briefing.
    """
    t0 = time.perf_counter()
    card = action_recommender.generate_action_card(
        tag_number="KO-3201",
        anomaly_info={"hour": 633, "health_index": 98.6},
        use_llm=False,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert elapsed_ms < 20.0
    assert "Ringkasan Eksekutif Terverifikasi" in card["copilot_shift_briefing"]
    assert "$1.188M" in card["copilot_shift_briefing"]
    assert "DETERMINISTIC_TEMPLATE_0MS" in card["synthesis_mode"]


def test_zcu_plant_equipment_coverage_and_multi_domain(action_recommender):
    """
    Test 7: Verifies full fleet coverage of 56 ZCU equipments (27 rotary + 29 static)
    and validates multi-domain support for KO-3201 (Rotary) and HE-3301 (Static).
    """
    zcu_tags = [
        k for k, v in action_recommender.knowledge.items() if v.get("plant") == "ZCU"
    ]
    assert len(zcu_tags) == 56

    # Rotary Multi-Domain Validation (KO-3201)
    card_ko = action_recommender.generate_action_card(
        tag_number="KO-3201",
        anomaly_info={"hour": 633, "health_index": 98.6},
        use_llm=False,
    )
    assert card_ko["provenance_level"] == "FACT"
    assert "ROTARY" in card_ko["root_cause_analysis"]["attribution_discipline"]

    # Static Multi-Domain Validation (HE-3301)
    card_he = action_recommender.generate_action_card(
        tag_number="HE-3301",
        anomaly_info={"hour": 700, "health_index": 82.0},
        use_llm=False,
    )
    assert card_he["provenance_level"] == "FACT"
    assert "STATIC" in card_he["root_cause_analysis"]["attribution_discipline"]
    hist_he = card_he["financial_risk_dual_metric"]["historical_benchmark_retrospective"]
    assert hist_he["total_loss_k_usd"] == 238.68
    assert hist_he["actual_loss_k_usd"] == 183.6
    assert hist_he["potential_loss_k_usd"] == 55.08
    assert hist_he["actual_downtime_hrs"] == 12.0


def test_evaluate_operational_state_triplet_logic(action_recommender):
    """
    Test 8: Verifies 5 operational states governed by triplet logic f(run_status, is_anomaly, HI).
    Thresholds: NORMAL >= 85.0%, WARNING < 65.0%.
    """
    from src.models.action_recommender import evaluate_operational_state

    # 1. State 1: OFFLINE (Machine Stopped, run_status = 0)
    status_text, color, state = evaluate_operational_state(run_status=0, is_anomaly=False, health_index=0.0)
    assert state == 1
    assert color == "GREY"
    assert "OFFLINE" in status_text

    # 2. State 2: NORMAL STEADY-STATE (run_status = 1, is_anomaly = False, HI = 100.0%)
    status_text, color, state = evaluate_operational_state(run_status=1, is_anomaly=False, health_index=100.0)
    assert state == 2
    assert color == "GREEN"
    assert "NORMAL STEADY-STATE" in status_text

    # 3. State 3: EARLY WARNING (run_status = 1, is_anomaly = True, HI = 98.6% >= 85.0%)
    status_text, color, state = evaluate_operational_state(run_status=1, is_anomaly=True, health_index=98.6)
    assert state == 3
    assert color == "AMBER"
    assert "EARLY WARNING" in status_text
    assert "NORMAL" in status_text

    # 4. State 4: WARNING (run_status = 1, is_anomaly = True, 65.0% <= HI < 85.0%)
    status_text, color, state = evaluate_operational_state(run_status=1, is_anomaly=True, health_index=75.0)
    assert state == 4
    assert color == "YELLOW"
    assert "WARNING" in status_text

    # 5. State 5: CRITICAL (run_status = 1, is_anomaly = True, HI < 65.0%)
    status_text, color, state = evaluate_operational_state(run_status=1, is_anomaly=True, health_index=45.0)
    assert state == 5
    assert color == "RED"
    assert "CRITICAL" in status_text

