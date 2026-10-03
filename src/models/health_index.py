"""
Equipment Health Index Engine (0 - 100%).
Mengacu pada ISO 10816-3 dan referensi paper arXiv:2405.04990.

Penalty per parameter (0-100) is the distance from `normal` towards `trip`,
respecting the limit direction (upper: rising is bad, lower: falling is bad).
A weighted sum gives the base penalty; a single parameter deep in the red
zone (>= 85%) escalates the total (worst-case limiting factor).
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "config" / "equipment_config.json"

ESCALATION_TRIGGER = 85.0  # % penalty of the worst parameter that triggers escalation
ESCALATION_FACTOR = 0.75
NORMAL_MIN = 85.0
WARNING_MIN = 65.0


def classify(hi: float) -> str:
    if hi >= NORMAL_MIN:
        return "NORMAL"
    if hi >= WARNING_MIN:
        return "WARNING"
    return "CRITICAL"


class HealthIndexCalculator:
    def __init__(self, config_path: Optional[str] = None, equipment_tag: str = "KO-3201"):
        with open(config_path or DEFAULT_CONFIG, encoding="utf-8") as f:
            cfg = json.load(f)[equipment_tag]
        self.equipment_tag = equipment_tag
        self.parameters: Dict[str, dict] = cfg["parameters"]

    def _penalty(self, cfg: dict, val: float) -> float:
        norm, trip = cfg["normal"], cfg["trip"]
        if cfg.get("direction", "upper") == "upper":
            pen = (val - norm) / (trip - norm) * 100.0 if trip > norm else 0.0
        else:
            pen = (norm - val) / (norm - trip) * 100.0 if norm > trip else 0.0
        return min(100.0, max(0.0, pen))

    def calculate_row(self, row: dict) -> Tuple[float, str, Dict[str, float]]:
        """Return (health_index, status, per-parameter penalties)."""
        if row.get("RUN_STATUS", 1) == 0:
            return 0.0, "OFFLINE", {"offline": 100.0}

        penalties = {
            p: self._penalty(cfg, row[p])
            for p, cfg in self.parameters.items()
            if p in row and pd.notna(row[p])
        }
        base = sum(self.parameters[p]["weight"] * pen for p, pen in penalties.items())
        worst = max(penalties.values(), default=0.0)
        total = max(base, ESCALATION_FACTOR * worst) if worst >= ESCALATION_TRIGGER else base
        hi = max(0.0, 100.0 - total)
        return hi, classify(hi), penalties

    def predict_step(self, current_row, history_window_df: Optional[pd.DataFrame] = None) -> dict:
        """Single-row evaluation for the streaming dashboard (history is unused: HI is memoryless)."""
        hi, status, penalties = self.calculate_row(dict(current_row))
        return {"health_index": hi, "status": status, "penalties": penalties}

    def evaluate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a copy of df with HEALTH_INDEX and HEALTH_STATUS columns."""
        out = df.copy()
        results = [self.calculate_row(r) for r in df.to_dict("records")]
        out["HEALTH_INDEX"] = [r[0] for r in results]
        out["HEALTH_STATUS"] = [r[1] for r in results]
        return out
