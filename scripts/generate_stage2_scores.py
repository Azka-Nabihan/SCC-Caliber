"""
Generate pre-computed Stage 2 scores for KO-3201 (720 hours).
Output: data/processed/KO3201_stage2_scores.csv (~85 KB)

Ensures zero-torch runtime for Streamlit dashboard, sub-2ms responsiveness,
and zero data-leakage / memory overhead.
"""

import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.models.gdn_detector import GDNDetector
from src.models.health_index import HealthIndexCalculator

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "processed" / "KO3201_cleaned.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "KO3201_stage2_scores.csv"


def main():
    print(f"Loading raw telemetry from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    assert len(df) == 720, f"Expected 720 rows, got {len(df)}"

    print("Fitting GDNDetector on baseline hours 0-500...")
    detector = GDNDetector()
    detector.fit(df.iloc[:500])

    print("Executing full 720-hour GDN inference...")
    scores_df = detector.detect(df)

    print("Computing Health Index series...")
    hi_calc = HealthIndexCalculator()
    hi_results = [hi_calc.calculate_row(r) for r in df.to_dict("records")]
    hi_scores = [round(r[0], 2) for r in hi_results]

    # Build top contributors list for each row
    top_contributors_list = []
    for i in range(len(df)):
        if i < detector.win:
            top_contributors_list.append("[]")
        else:
            top_c = detector.get_top_contributors(i, top_k=2)
            top_contributors_list.append(json.dumps([[k, round(v, 2)] for k, v in top_c]))

    # Construct clean, combined output DataFrame
    out_df = pd.DataFrame({
        "timestamp": df["Timestamp"],
        "hour": np.arange(len(df)),
        "RUN_STATUS": df["RUN_STATUS"].astype(int),
        "KO3201_FEED": df["KO3201_FEED"].round(2),
        "KO3201_DISP": df["KO3201_DISP"].round(2),
        "KO3201_AMP": df["KO3201_AMP"].round(2),
        "KO3201_TEMP": df["KO3201_TEMP"].round(2),
        "KO3201_VIB": df["KO3201_VIB"].round(2),
        "PLANT_RATE": df["PLANT_RATE"].round(2),
        "gdn_anomaly_score": scores_df["anomaly_score"].round(4),
        "is_anomaly": scores_df["is_anomaly"].astype(bool),
        "top_contributors": top_contributors_list,
        "health_index": hi_scores
    })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Successfully generated {OUTPUT_PATH} ({len(out_df)} rows, {OUTPUT_PATH.stat().st_size / 1024:.1f} KB)")

    # Verification assertions
    hr633 = out_df.iloc[633]
    print("\n--- Hour 633 Verification ---")
    print(f"Timestamp: {hr633['timestamp']}")
    print(f"GDN Anomaly Score: {hr633['gdn_anomaly_score']} (Expected ~10.72)")
    print(f"Is Anomaly: {hr633['is_anomaly']} (Expected True)")
    print(f"Top Contributors: {hr633['top_contributors']} (Expected KO3201_VIB)")
    print(f"Health Index: {hr633['health_index']}% (Expected 98.58%)")
    print(f"Vibration: {hr633['KO3201_VIB']} um (Expected 31.24 um)")

    assert hr633["is_anomaly"] is True or hr633["is_anomaly"] == 1, "Hour 633 must be anomaly!"
    assert 10.0 <= hr633["gdn_anomaly_score"] <= 11.5, f"Anomaly score mismatch: {hr633['gdn_anomaly_score']}"
    assert 98.0 <= hr633["health_index"] <= 99.0, f"Health index mismatch: {hr633['health_index']}"
    print("Verification Passed 100%!")


if __name__ == "__main__":
    main()
