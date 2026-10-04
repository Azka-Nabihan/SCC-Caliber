"""
Incident Matcher & Process Physics Engine for SCC-Caliber.
Implements 3-tier hierarchical matching with temporal data-leakage prevention
and deterministic physical process loss estimation for industrial equipment.
"""

from pathlib import Path
import json
from typing import Any, Dict, Optional, Union
import numpy as np
import pandas as pd

from src.pipeline.incident_loader import IncidentLoader


class IncidentMatcher:
    """
    Hierarchical Incident Matcher for estimating financial exposure and downtime.
    
    Matching Tiers:
    - Tier 1: Exact Composite Match (Plant, Tag Number)
    - Tier 2: Component Fallback within same Plant (n >= 3 condition)
    - Tier 3: Equipment Fleet Class Fallback (Class A/B/C or Overall Refinery Median)
    """

    def __init__(
        self,
        incidents_df: Optional[pd.DataFrame] = None,
        zcu_knowledge_path: Optional[Union[str, Path]] = None,
    ):
        project_root = Path(__file__).resolve().parents[2]

        if incidents_df is not None:
            self.df = incidents_df.copy()
        else:
            loader = IncidentLoader()
            self.df = loader.get_cleaned_df()

        if zcu_knowledge_path is None:
            self.knowledge_path = project_root / "src" / "config" / "rca_knowledge.json"
        else:
            self.knowledge_path = Path(zcu_knowledge_path)

        self.knowledge: Dict[str, Any] = {}
        if self.knowledge_path.exists():
            try:
                with open(self.knowledge_path, "r", encoding="utf-8") as f:
                    self.knowledge = json.load(f)
            except Exception:
                self.knowledge = {}

    def estimate_process_loss(
        self,
        downtime_hrs: float,
        plant_rate_t_per_hr: float = 55.0,
        product_price_per_ton: float = 900.0,
    ) -> Dict[str, float]:
        """
        Calculates deterministic physical production loss:
        Loss (USD) = Downtime (hrs) x Production Rate (T/H) x Product Price ($/ton)
        """
        tonnage_lost = float(downtime_hrs * plant_rate_t_per_hr)
        loss_usd = float(tonnage_lost * product_price_per_ton)
        return {
            "downtime_hrs": float(downtime_hrs),
            "plant_rate_t_per_hr": float(plant_rate_t_per_hr),
            "product_price_per_ton": float(product_price_per_ton),
            "tonnage_lost": round(tonnage_lost, 2),
            "calculated_loss_k_usd": round(loss_usd / 1000.0, 2),
        }

    def match(
        self,
        plant: str,
        tag_number: str,
        component: Optional[str] = None,
        eq_class: Optional[str] = None,
        as_of: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes 3-tier hierarchical matching with temporal cutoff.
        """
        plant_clean = str(plant).strip().upper()
        tag_clean = str(tag_number).strip().upper()

        # Step 0: Apply as_of filter to prevent temporal leakage
        working_df = self.df.copy()
        if as_of is not None:
            as_of_dt = pd.to_datetime(as_of)
            working_df = working_df[
                pd.to_datetime(working_df["occur_date"]) < as_of_dt
            ]

        # Tier 1: Exact Composite Match (plant, tag_number)
        t1_matches = working_df[
            (working_df["plant"] == plant_clean)
            & (working_df["tag_number"] == tag_clean)
        ]

        if not t1_matches.empty:
            # Take the most recent incident before as_of
            matched_rec = t1_matches.iloc[-1]
            return {
                "match_tier": 1,
                "match_level": "EXACT_TAG",
                "incident_reference": str(matched_rec.get("ar_no", "N/A")),
                "occur_date": str(matched_rec.get("occur_date", "N/A")),
                "actual_downtime_hrs": float(matched_rec.get("downtime_hrs", 0.0)),
                "actual_loss_k_usd": float(matched_rec.get("actual_loss_k_usd", 0.0)),
                "potential_loss_k_usd": float(matched_rec.get("potential_loss_k_usd", 0.0)),
                "total_loss_k_usd": float(matched_rec.get("total_loss_k_usd", 0.0)),
                "sample_size": len(t1_matches),
                "details": f"Exact composite match on plant {plant_clean} and tag {tag_clean}",
            }

        # Lookup component and eq_class from knowledge store if missing
        if component is None and tag_clean in self.knowledge:
            component = self.knowledge[tag_clean].get("root_cause_summary", {}).get("physical_trigger")

        if eq_class is None and tag_clean in self.knowledge:
            eq_class = self.knowledge[tag_clean].get("eq_class")

        # Tier 2: Component Fallback within same Plant (requires n >= 3)
        if component:
            comp_clean = str(component).strip().upper()
            t2_matches = working_df[
                (working_df["plant"] == plant_clean)
                & (working_df["component"] == comp_clean)
            ]
            if len(t2_matches) >= 3:
                med_dt = float(t2_matches["downtime_hrs"].median())
                med_total_loss = float(t2_matches["total_loss_k_usd"].median())
                med_act_loss = float(t2_matches["actual_loss_k_usd"].median())
                med_pot_loss = float(t2_matches["potential_loss_k_usd"].median())
                p25_loss = float(t2_matches["total_loss_k_usd"].quantile(0.25))
                p75_loss = float(t2_matches["total_loss_k_usd"].quantile(0.75))

                return {
                    "match_tier": 2,
                    "match_level": "COMPONENT_PLANT",
                    "incident_reference": f"MEDIAN_TIER2_{plant_clean}_{comp_clean}",
                    "occur_date": None,
                    "actual_downtime_hrs": round(med_dt, 2),
                    "actual_loss_k_usd": round(med_act_loss, 2),
                    "potential_loss_k_usd": round(med_pot_loss, 2),
                    "total_loss_k_usd": round(med_total_loss, 2),
                    "p25_loss_k_usd": round(p25_loss, 2),
                    "p75_loss_k_usd": round(p75_loss, 2),
                    "sample_size": len(t2_matches),
                    "details": f"Component-level median fallback in {plant_clean} (n={len(t2_matches)})",
                }

        # Tier 3: Equipment Class Fallback (Class A, B, C or Refinery Unclassified)
        eq_class_clean = str(eq_class).strip().upper() if eq_class else "A"
        if eq_class_clean in ["A", "B", "C"]:
            t3_matches = working_df[working_df["eq_class"] == eq_class_clean]
        else:
            t3_matches = pd.DataFrame()

        if not t3_matches.empty:
            med_dt = float(t3_matches["downtime_hrs"].median())
            med_total_loss = float(t3_matches["total_loss_k_usd"].median())
            med_act_loss = float(t3_matches["actual_loss_k_usd"].median())
            med_pot_loss = float(t3_matches["potential_loss_k_usd"].median())
            p25_loss = float(t3_matches["total_loss_k_usd"].quantile(0.25))
            p75_loss = float(t3_matches["total_loss_k_usd"].quantile(0.75))

            return {
                "match_tier": 3,
                "match_level": f"CLASS_{eq_class_clean}",
                "incident_reference": f"MEDIAN_CLASS_{eq_class_clean}",
                "occur_date": None,
                "actual_downtime_hrs": round(med_dt, 2),
                "actual_loss_k_usd": round(med_act_loss, 2),
                "potential_loss_k_usd": round(med_pot_loss, 2),
                "total_loss_k_usd": round(med_total_loss, 2),
                "p25_loss_k_usd": round(p25_loss, 2),
                "p75_loss_k_usd": round(p75_loss, 2),
                "sample_size": len(t3_matches),
                "details": f"Equipment Class {eq_class_clean} fleet fallback",
            }

        # Tier 3 Final Fallback: Entire Refinery Median
        med_dt = float(working_df["downtime_hrs"].median())
        med_total_loss = float(working_df["total_loss_k_usd"].median())
        med_act_loss = float(working_df["actual_loss_k_usd"].median())
        med_pot_loss = float(working_df["potential_loss_k_usd"].median())
        p25_loss = float(working_df["total_loss_k_usd"].quantile(0.25))
        p75_loss = float(working_df["total_loss_k_usd"].quantile(0.75))

        return {
            "match_tier": 3,
            "match_level": "UNCLASSIFIED_OVERALL",
            "incident_reference": "MEDIAN_REFINERY_OVERALL",
            "occur_date": None,
            "actual_downtime_hrs": round(med_dt, 2),
            "actual_loss_k_usd": round(med_act_loss, 2),
            "potential_loss_k_usd": round(med_pot_loss, 2),
            "total_loss_k_usd": round(med_total_loss, 2),
            "p25_loss_k_usd": round(p25_loss, 2),
            "p75_loss_k_usd": round(p75_loss, 2),
            "sample_size": len(working_df),
            "details": "Refinery-wide unclassified overall median fallback",
        }
