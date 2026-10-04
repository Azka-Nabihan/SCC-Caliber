"""
Unit tests for Phase 2: Equipment Reliability KPIs & Past Similar Incidents.
Validates dynamic calculation of Availability, MTBF, MTTR, Maintenance Compliance,
and high-relevance similar historical incidents matching.
"""

import pytest
from src.app.data_provider import DashboardDataProvider


@pytest.fixture
def provider():
    return DashboardDataProvider()


def test_reliability_kpis_normal_states(provider):
    """
    Verifies that reliability KPIs for Hours 100, 633, and 649 reflect steady-state operational uptime:
    Availability: 98.4%, Downtime: 0.0h, Production loss: $0.0k.
    """
    for hr in [100, 633, 649]:
        kpi = provider.get_pilot_reliability_kpis(hr)
        assert kpi["current_hour"] == hr
        assert kpi["is_tripped"] is False
        assert kpi["availability_pct"] == pytest.approx(98.4, abs=0.01)
        assert kpi["availability_target_pct"] == pytest.approx(96.0, abs=0.01)
        assert kpi["mtbf_hrs"] == 1420
        assert kpi["mtbf_days"] == pytest.approx(59.2, abs=0.1)
        assert kpi["mttr_planned_hrs"] == 8.0
        assert kpi["mttr_emergency_hrs"] == 32.0
        assert kpi["maintenance_compliance_pct"] == pytest.approx(94.2, abs=0.01)
        assert kpi["total_downtime_hrs"] == 0.0
        assert kpi["production_loss_k_usd"] == 0.0
        assert kpi["lost_production_tons"] == 0.0
        assert kpi["machine_status"] == "STEADY_RUNNING"


def test_reliability_kpis_tripped_state(provider):
    """
    Verifies that reliability KPIs for Hour 679 (Post-trip) reflect the outage penalty:
    Availability: drops to 95.6%, Downtime: 32.0h, Production loss: $1,584.0k (1,760 tons).
    """
    kpi = provider.get_pilot_reliability_kpis(679)
    assert kpi["current_hour"] == 679
    assert kpi["is_tripped"] is True
    assert kpi["availability_pct"] == pytest.approx(95.6, abs=0.01)
    assert kpi["mtbf_hrs"] == 1420
    assert kpi["total_downtime_hrs"] == 32.0
    assert kpi["production_loss_k_usd"] == pytest.approx(1584.0, abs=0.1)
    assert kpi["lost_production_tons"] == pytest.approx(1760.0, abs=0.1)
    assert kpi["machine_status"] == "TRIPPED_OUTAGE"


def test_similar_incidents_structure_and_matching(provider):
    """
    Verifies that similar incidents retrieval provides top-3 matches with similarity scores,
    downtime, and financial loss context.
    """
    incidents = provider.get_similar_incidents(equipment_type="COMPRESSOR", top_k=3)
    assert len(incidents) == 3

    top = incidents[0]
    assert top["incident_reference"] == "AR-2026-ZCU-0142"
    assert top["tag_number"] == "KO-3201"
    assert top["actual_downtime_hrs"] == 32.0
    assert top["actual_loss_k_usd"] == pytest.approx(1584.0, abs=0.1)
    assert top["similarity_pct"] == 96

    second = incidents[1]
    assert second["incident_reference"] == "AR-2025-SMX-0164"
    assert second["similarity_pct"] == 88

    third = incidents[2]
    assert third["incident_reference"] == "MTO-2025-SMX-0138"
    assert third["similarity_pct"] == 82
