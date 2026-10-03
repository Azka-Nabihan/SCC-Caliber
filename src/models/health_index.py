"""
Equipment Health Index Engine (0 - 100%).
Mengacu pada ISO 10816-3 dan referensi paper arXiv:2405.04990.
"""

from typing import Dict


class HealthIndexCalculator:
    def __init__(self, weights: Dict[str, float], thresholds: Dict[str, Dict[str, float]]):
        """
        weights: bobot variabel (misal: {'vibration': 0.4, 'temp': 0.3, 'pressure': 0.3})
        thresholds: batas normal, alarm, trip per variabel
        """
        self.weights = weights
        self.thresholds = thresholds

    def calculate(self, current_metrics: Dict[str, float]) -> float:
        score = 100.0
        for param, val in current_metrics.items():
            if param in self.thresholds:
                limits = self.thresholds[param]
                if val >= limits.get("trip", float("inf")):
                    penalty = 50.0 * self.weights.get(param, 0.2)
                elif val >= limits.get("alarm", float("inf")):
                    penalty = 25.0 * self.weights.get(param, 0.2)
                else:
                    penalty = 0.0
                score -= penalty
        return max(0.0, min(100.0, score))
