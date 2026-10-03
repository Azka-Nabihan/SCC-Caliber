import numpy as np
import pandas as pd
import pytest
import torch

from src.models.gdn_detector import SENSOR_NODES, GDNDetector, build_edge_index
from src.models.health_index import HealthIndexCalculator

DCS_ALARM_HOUR = 649  # first hour KO3201_VIB >= 45 micron
TRIP_HOUR = 679  # first RUN_STATUS == 0


@pytest.fixture(scope="module")
def df():
    return pd.read_csv("data/processed/KO3201_cleaned.csv")


@pytest.fixture(scope="module")
def hi_df(df):
    return HealthIndexCalculator().evaluate_dataframe(df)


@pytest.fixture(scope="module")
def gdn(df):
    d = GDNDetector()
    d.fit(df.iloc[:500], weights_path=None)
    d.result = d.detect(df)
    return d


def test_health_index_normal_state(hi_df):
    assert hi_df["HEALTH_INDEX"].iloc[:100].min() > 85
    assert (hi_df["HEALTH_STATUS"].iloc[:100] == "NORMAL").all()


def test_health_index_directionality():
    hi = HealthIndexCalculator()
    # FEED is a lower-limit sensor: above normal -> no penalty, below normal -> penalty
    assert hi._penalty(hi.parameters["KO3201_FEED"], 70.0) == 0.0
    assert hi._penalty(hi.parameters["KO3201_FEED"], 40.0) > 0.0
    assert hi._penalty(hi.parameters["KO3201_FEED"], 20.0) == 100.0
    assert hi._penalty(hi.parameters["KO3201_VIB"], 10.0) == 0.0


def test_health_index_offline_guardrail(hi_df):
    assert hi_df.loc[680, "HEALTH_INDEX"] == 0.0
    assert hi_df.loc[680, "HEALTH_STATUS"] == "OFFLINE"


def test_health_index_pre_trip_critical(hi_df):
    assert hi_df.loc[678, "HEALTH_INDEX"] < 45
    assert hi_df.loc[678, "HEALTH_STATUS"] == "CRITICAL"


def test_gdn_determinism_seed(df):
    runs = []
    for _ in range(2):
        d = GDNDetector()
        losses = d.fit(df.iloc[:500], epochs=5, weights_path=None)
        runs.append((losses, d.tau, d.detect(df.iloc[:520])["anomaly_score"].values))
    assert runs[0][0] == runs[1][0]
    assert runs[0][1] == runs[1][1]
    np.testing.assert_array_equal(runs[0][2], runs[1][2])


def test_gdn_node_index_mapping():
    edges = [["PLANT_RATE", "KO3201_FEED"], ["KO3201_TEMP", "KO3201_VIB"]]
    ei = build_edge_index(edges)
    assert ei.tolist() == [[0, 4], [1, 5]]
    d = GDNDetector()
    assert d.nodes == SENSOR_NODES
    assert d.edge_index.shape == (2, 6)
    assert d.edge_index.max() == len(SENSOR_NODES) - 1
    adj = d.model.adj  # adj[target, source]
    assert adj[5, 4] and not adj[4, 5]  # TEMP -> VIB is directed
    assert adj.diagonal().all()


def test_gdn_training_objective_threshold(gdn):
    r = gdn.result.iloc[:500]
    assert gdn.tau == pytest.approx(np.percentile(r["anomaly_score"].dropna(), 99.5), rel=0.05)
    assert r["is_anomaly"].sum() == 0  # no persistent false alarm on normal training data


def test_gdn_alarm_persistence(df):
    d = GDNDetector()
    d.fit(df.iloc[:500], epochs=5, weights_path=None)
    # a single-hour spike in VIB must not raise a persistent alarm
    spike = df.iloc[:60].copy()
    spike.loc[40, "KO3201_VIB"] += 15
    r = d.detect(spike)
    assert r["raw_exceed"].sum() >= 1
    assert r["raw_exceed"].sum() < 3  # spike hits t and t+1 (window) at most
    assert not r["is_anomaly"].iloc[40]
    # a sustained shift must
    shift = df.iloc[:60].copy()
    shift.loc[40:, "KO3201_VIB"] += 15
    assert d.detect(shift)["is_anomaly"].iloc[41:].all()


def test_gdn_early_detection_lead_time(gdn):
    alarms = np.where(gdn.result["is_anomaly"].values[:TRIP_HOUR])[0]
    first = alarms.min()
    assert 600 <= first <= 645
    assert DCS_ALARM_HOUR - first >= 8
    assert gdn.get_top_contributors(first)[0][0] == "KO3201_VIB"


def test_gdn_no_alarm_after_restart(gdn):
    assert not gdn.result["is_anomaly"].iloc[679:].any()


def test_predict_step_streaming_interface(df, gdn):
    t = 645
    step = gdn.predict_step(df.iloc[t], df.iloc[t - 24:t])
    assert step["is_anomaly"]
    assert step["top_contributors"][0][0] == "KO3201_VIB"
    hi = HealthIndexCalculator().predict_step(df.iloc[t], df.iloc[t - 24:t])
    assert 0 <= hi["health_index"] <= 100
