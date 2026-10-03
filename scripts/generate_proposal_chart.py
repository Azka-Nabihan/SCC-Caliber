"""Run the Stage 2 pipeline on KO-3201 and save the proposal validation chart."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.models.gdn_detector import GDNDetector
from src.models.health_index import HealthIndexCalculator

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed" / "KO3201_stage2_validation.png"
TRAIN_HOURS = 500
DCS_ALARM, VIB_TRIP = 45.0, 75.0

df = pd.read_csv(ROOT / "data" / "processed" / "KO3201_cleaned.csv", parse_dates=["Timestamp"])
det = GDNDetector()
det.fit(df.iloc[:TRAIN_HOURS])
res = det.detect(df)
hi = HealthIndexCalculator().evaluate_dataframe(df)

trip_h = int(np.argmax(df["RUN_STATUS"].values == 0))
dcs_h = int(np.argmax(df["KO3201_VIB"].values >= DCS_ALARM))
gdn_h = int(np.argmax(res["is_anomaly"].values[:trip_h]))
ts = lambda h: df["Timestamp"].iloc[h]

print(f"GDN early warning : hour {gdn_h} ({ts(gdn_h)})")
print(f"DCS alarm (45 um) : hour {dcs_h} ({ts(dcs_h)}) -> lead time {dcs_h - gdn_h} h")
print(f"Trip              : hour {trip_h} ({ts(trip_h)}) -> reaction time before trip {trip_h - gdn_h} h")
print(f"Persistent false alarms in training window: {int(res['is_anomaly'].iloc[:TRAIN_HOURS].sum())}")
print(f"Top contributors at warning: {det.get_top_contributors(gdn_h)}")

x = df["Timestamp"]
lo = trip_h - 120
fig, ax = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
ax[0].plot(x, df["KO3201_VIB"], color="tab:blue")
ax[0].axhline(DCS_ALARM, color="orange", ls="--", label="DCS alarm 45 um")
ax[0].axhline(VIB_TRIP, color="red", ls="--", label="Trip 75 um")
ax[0].set_ylabel("DE radial vibration (um)")
ax[0].legend(loc="upper left")

score = res["anomaly_score"].where(df["RUN_STATUS"] == 1).clip(lower=0.1)  # offline scores are meaningless
ax[1].plot(x, score, color="tab:purple")
ax[1].axhline(det.tau, color="gray", ls=":", label=f"tau = P99.5 train = {det.tau:.2f}")
ax[1].axvline(ts(gdn_h), color="green", label=f"GDN early warning (h{gdn_h})")
ax[1].axvline(ts(dcs_h), color="orange", label=f"DCS alarm (h{dcs_h}), lead {dcs_h - gdn_h} h")
ax[1].set_yscale("log")
ax[1].set_ylabel("GDN anomaly score")
ax[1].legend(loc="upper left")

ax[2].plot(x, hi["HEALTH_INDEX"], color="tab:green")
ax[2].axhline(85, color="gray", ls=":")
ax[2].axhline(65, color="gray", ls=":")
ax[2].set_ylabel("Health Index (%)")
ax[2].set_ylim(-5, 105)

for a in ax:
    a.axvline(ts(trip_h), color="red", alpha=0.4)
    a.set_xlim(x.iloc[lo], x.iloc[-1])
fig.suptitle("KO-3201 Stage 2 validation: GDN early warning vs DCS alarm, with Health Index")
fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, dpi=150)
print(f"Saved {OUT}")
