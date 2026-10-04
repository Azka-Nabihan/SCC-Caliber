"""
Unit tests for Phase 3: Fleet Pareto Analysis & Root Cause Breakdown (4M+1E / 4P).
Validates failure mechanisms Pareto aggregation, top bad actors ranking (with KO-3201 #1),
and structured root cause matrix retrieval.
"""

import pytest
import plotly.graph_objects as go
from src.app.data_provider import DashboardDataProvider
from src.app.charts import create_pareto_chart


@pytest.fixture
def provider():
    return DashboardDataProvider()


def test_pareto_failure_mechanisms(provider):
    """
    Verifies that failure mechanisms aggregation correctly ranks top causes
    across the 380 incidents:
    - Leakage is #1 with ~$15.6M ($15,641k) loss
    - High Vibration is #2 with ~$9.1M ($9,128k) loss
    - Returns proper cumulative percentage curve up to 8 items
    """
    df = provider.get_pareto_failure_mechanisms(top_n=8)
    assert len(df) == 8
    assert "f_mechanism" in df.columns
    assert "loss_k_usd" in df.columns
    assert "cumulative_loss_pct" in df.columns

    # Verify #1 and #2 failure causes
    assert df.iloc[0]["f_mechanism"] == "Leakage"
    assert df.iloc[0]["loss_k_usd"] == pytest.approx(15641.0, rel=1e-2)
    assert df.iloc[1]["f_mechanism"] == "High Vibration"
    assert df.iloc[1]["loss_k_usd"] == pytest.approx(9128.4, rel=1e-2)

    # Cumulative percentage should be monotonically increasing
    cum_pcts = df["cumulative_loss_pct"].tolist()
    assert all(cum_pcts[i] <= cum_pcts[i + 1] for i in range(len(cum_pcts) - 1))
    assert 0 < cum_pcts[0] < 100


def test_pareto_bad_actors(provider):
    """
    Verifies that top bad actors aggregation correctly identifies Pilot Asset KO-3201
    as the #1 financial loss equipment ($1,584.0k, 32.0h downtime) across the entire complex.
    """
    df = provider.get_pareto_bad_actors(top_n=10)
    assert len(df) == 10
    assert "tag_number" in df.columns
    assert "plant" in df.columns
    assert "loss_k_usd" in df.columns
    assert "is_pilot" in df.columns

    # #1 Bad Actor must be KO-3201 in ZCU
    top_actor = df.iloc[0]
    assert top_actor["tag_number"] == "KO-3201"
    assert top_actor["plant"] == "ZCU"
    assert top_actor["loss_k_usd"] == pytest.approx(1584.0, abs=0.1)
    assert top_actor["downtime_hrs"] == pytest.approx(32.0, abs=0.1)
    assert bool(top_actor["is_pilot"]) is True

    # #2 is TX-5187B in SMX
    assert df.iloc[1]["tag_number"] == "TX-5187B"
    assert df.iloc[1]["plant"] == "SMX"


def test_root_cause_matrix_frameworks(provider):
    """
    Verifies that get_root_cause_matrix supports both 4M+1E (5 categories)
    and 4P (4 categories) frameworks with complete evidence and mitigation fields.
    """
    m41e = provider.get_root_cause_matrix(framework="4M1E")
    assert len(m41e) == 5
    categories_4m = [item["category"] for item in m41e]
    assert "MACHINE" in categories_4m
    assert "MATERIAL" in categories_4m
    assert "METHOD" in categories_4m
    assert "MAN" in categories_4m
    assert "ENVIRONMENT" in categories_4m

    for item in m41e:
        assert "finding" in item
        assert "status" in item
        assert "evidence" in item
        assert "mitigation" in item
        assert "color" in item

    p4 = provider.get_root_cause_matrix(framework="4P")
    assert len(p4) == 4
    categories_4p = [item["category"] for item in p4]
    assert "PLANT" in categories_4p
    assert "PROCESS" in categories_4p
    assert "PEOPLE" in categories_4p
    assert "PROGRAM" in categories_4p


def test_create_pareto_chart_rendering(provider):
    """
    Verifies that create_pareto_chart creates valid Plotly Figure objects
    for both failure mechanisms view and bad actors view.
    """
    df_mech = provider.get_pareto_failure_mechanisms(top_n=8)
    fig_mech = create_pareto_chart(df_mech, view_type="mechanism")
    assert isinstance(fig_mech, go.Figure)
    assert len(fig_mech.data) == 2  # 1 Bar trace + 1 Scatter line trace

    df_actors = provider.get_pareto_bad_actors(top_n=10)
    fig_actors = create_pareto_chart(df_actors, view_type="bad_actors")
    assert isinstance(fig_actors, go.Figure)
    assert len(fig_actors.data) == 2
