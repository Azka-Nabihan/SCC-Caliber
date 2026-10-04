"""
Interactive Terminal Demonstration Runner for SCC-Caliber Stage 3.
Presents the executive Action Card at hour 633 for Cracked Gas Compressor KO-3201:
- Early GDN Anomaly Signal & Health Index (98.6% NORMAL - AMBER)
- 16-Hour Lead Time before DCS Alarm
- Dual-Metric Financial Risk & $1.188M Cost Avoidance
- Verbatim Operator SOP & Engineering CAPA (100% Provenance)
- Operational Copilot Shift Briefing Narration

Saves generated payload to data/processed/KO3201_stage3_action_card.json.
"""

import sys
from pathlib import Path

# Mandatory root path injection
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import pandas as pd

from src.models.action_recommender import ActionRecommender
from src.pipeline.replay_loader import ReplayLoader


def run_stage3_demo():
    print("\n" + "=" * 80)
    print("  SCC-CALIBER: STAGE 3 CONTEXTUALIZATION & PRESCRIPTIVE RCA ENGINE")
    print("  Chandra Asri Petrochemical - Plant ZCU (Olefin Cracker Unit)")
    print("=" * 80)

    # 1. Load telemetry signal at Hour 633
    cleaned_csv = Path("data/processed/KO3201_cleaned.csv")
    hour = 633
    vib_val = 31.2
    hi_val = 98.6
    gdn_score = 10.7

    if cleaned_csv.exists():
        df_sensor = pd.read_csv(cleaned_csv)
        if len(df_sensor) > hour:
            row = df_sensor.iloc[hour]
            vib_val = float(row.get("KO3201_VIB", vib_val))

    print(f"\n[1] REAL-TIME TELEMETRY & AI DETECTION SIGNAL (JAM KE-{hour})")
    print("-" * 80)
    print(f"  * Asset Tag         : KO-3201 (Cracked Gas Compressor - Class A)")
    print(f"  * P&ID Location     : Compression Train ZCU (Suction K.O. -> Stage 1)")
    print(f"  * Radial Vibration  : {vib_val:.1f} µm (Normal baseline: <30 µm, Alarm: 45 µm, Trip: 75 µm)")
    print(f"  * GDN Anomaly Score : {gdn_score:.1f} (Deviation from structural sensor correlation)")
    print(f"  * Health Index      : {hi_val:.1f}% -> Status: NORMAL (Amber Indicator)")

    # 2. Generate Action Card via ActionRecommender
    recommender = ActionRecommender()
    anomaly_info = {
        "hour": hour,
        "health_index": hi_val,
        "anomaly_score": gdn_score,
        "current_value": vib_val,
    }

    card = recommender.generate_action_card("KO-3201", anomaly_info, use_llm=True)

    # 3. Print Executive Action Card Summary
    print(f"\n[2] EXECUTIVE ACTION CARD PAYLOAD")
    print("-" * 80)
    print(f"  * Operational Status : \033[93m{card['current_status']}\033[0m")
    print(f"  * Indicator Color    : {card['status_color']}")
    print(f"  * Provenance Level   : \033[92m[{card['provenance_level']}]\033[0m (Official Plant RCA Documents)")
    print(f"  * Lead Time Official : \033[96m{card['detected_lead_time']['headline']}\033[0m")
    print(f"    Secondary Note     : {card['detected_lead_time']['secondary_note']}")

    # 4. Print Root Cause Analysis
    rca = card["root_cause_analysis"]
    print(f"\n[3] ROOT CAUSE ANALYSIS (TERVERIFIKASI)")
    print("-" * 80)
    print(f"  * Physical Trigger   : {rca['physical_trigger']}")
    print(f"  * Damage Mechanism   : {rca['damage_mechanism']}")
    print(f"  * Systemic Root Cause: {rca['systemic_latent_root_cause']}")
    print(f"  * Discipline         : {rca['attribution_discipline']}")

    # 5. Print Dual-Metric Financial Analysis
    dual_metric = card["financial_risk_dual_metric"]
    proc_sim = dual_metric["forward_looking_process_simulation"]
    hist_bench = dual_metric["historical_benchmark_retrospective"]

    print(f"\n[4] DUAL-METRIC FINANCIAL RISK ASSESSMENT")
    print("-" * 80)
    print("  (A) Forward-Looking Process Physics Simulation:")
    print(f"      Formula          : {proc_sim['formula']}")
    print(f"      Mitigated Case   : {proc_sim['controlled_shutdown_scenario']['estimated_downtime_hrs']} jam downtime -> "
          f"${proc_sim['controlled_shutdown_scenario']['estimated_loss_k_usd']:.1f}k USD "
          f"({proc_sim['controlled_shutdown_scenario']['description']})")
    print(f"      Uncontrolled Trip: {proc_sim['uncontrolled_trip_scenario']['estimated_downtime_hrs']} jam downtime -> "
          f"${proc_sim['uncontrolled_trip_scenario']['estimated_loss_k_usd']:.1f}k USD "
          f"({proc_sim['uncontrolled_trip_scenario']['description']})")
    print(f"      \033[92mPOTENSI PENGHEMATAN : ${proc_sim['potential_cost_savings_k_usd']:.1f}k USD "
          f"(${proc_sim['potential_cost_savings_k_usd']/1000.0:.3f} Juta)\033[0m")
    print()
    print("  (B) Historical Retrospective Benchmark (Single Truth):")
    print(f"      Incident Ref     : {hist_bench['incident_reference']} (Date: {hist_bench['occur_date']})")
    print(f"      Actual Downtime  : {hist_bench['actual_downtime_hrs']} jam")
    print(f"      Actual Loss      : ${hist_bench['actual_loss_k_usd']:.1f}k USD")
    print(f"      Potential Loss   : ${hist_bench['potential_loss_k_usd']:.1f}k USD")
    print(f"      Total Loss       : ${hist_bench['total_loss_k_usd']:.1f}k USD")

    # 6. Immediate Operator Actions
    print(f"\n[5] TINDAKAN DARURAT OPERATOR (< 30 MENIT)")
    print("-" * 80)
    for act in card["immediate_actions"]:
        print(f"  [{act['step']}] ({act['timeframe']}) {act['action']}")
        print(f"      \033[90mSource: {act['source']}\033[0m")

    # 7. Permanent Engineering CAPA
    print(f"\n[6] TINDAKAN PERMANEN ENGINEERING (CAPA)")
    print("-" * 80)
    for i, c in enumerate(card["permanent_capa"], 1):
        print(f"  ({i}) [{c['type']}] {c['action']}")
        print(f"      PIC: {c['pic']} | Due: {c['due_date']} | Status: {c['status']} | \033[90mSource: {c['source']}\033[0m")

    # 8. Operational Copilot Shift Briefing
    print(f"\n[7] OPERATIONAL COPILOT SHIFT BRIEFING")
    print("-" * 80)
    print(f"  * Mode   : \033[96m{card['synthesis_mode']}\033[0m")
    print(f"  * Narasi : \"{card['copilot_shift_briefing']}\"")

    # 9. Save Payload to JSON
    out_file = Path("data/processed/KO3201_stage3_action_card.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"  [SUCCESS] Action Card Payload saved to: {out_file}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_stage3_demo()
