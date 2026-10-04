"""
Incident Loader & Cleanser Pipeline for SCC-Caliber.
Ingests and standardizes 380 historical equipment failure incident records from
Chandra Asri's Incident Database with data integrity validation, type casting,
and persistent local caching.
"""

from pathlib import Path
from typing import Optional, Union
import pandas as pd


class IncidentLoader:
    """
    Cleanses and caches historical plant incident records across 12 petrochemical units.
    """

    COLUMN_MAPPING = {
        "Serial No": "serial_no",
        "MTO No.": "mto_no",
        "AR No.": "ar_no",
        "Plant": "plant",
        "Tag Number": "tag_number",
        "Eq. Class": "eq_class",
        "Date of Occur.": "occur_date",
        "Risk Case Title": "case_title",
        "Highest Impact": "highest_impact",
        "Pre-Risk": "pre_risk",
        "Risk Score": "risk_score",
        "PIC (RCA)": "pic_rca",
        "Overall Status": "overall_status",
        "Discipline": "discipline",
        "Eq. Type": "eq_type",
        "Component": "component",
        "F Mechanism": "f_mechanism",
        "Downtime (hrs)": "downtime_hrs",
        "Act. Loss (k US$)": "actual_loss_k_usd",
        "Pot. Loss (k US$)": "potential_loss_k_usd",
        "Total Loss (k US$)": "total_loss_k_usd",
        "RCA Due Date": "rca_due_date",
        "Month - Year": "month_year",
    }

    def __init__(
        self,
        raw_path: Optional[Union[str, Path]] = None,
        processed_path: Optional[Union[str, Path]] = None,
    ):
        project_root = Path(__file__).resolve().parents[2]
        
        if raw_path is None:
            self.raw_path = (
                project_root
                / "data"
                / "extracted"
                / "Supporting Data"
                / "Case 2_ Intelligence Manufacturing"
                / "Incident Database"
                / "Incident Database.xlsx"
            )
        else:
            self.raw_path = Path(raw_path)

        if processed_path is None:
            self.processed_path = (
                project_root / "data" / "processed" / "incidents_cleaned.csv"
            )
        else:
            self.processed_path = Path(processed_path)

    def load_and_clean(self) -> pd.DataFrame:
        """
        Reads raw Incident Database.xlsx (sheet 'Incident Database', header=2),
        standardizes column names, coerces numeric fields, formats dates,
        and saves cleansed output to CSV cache.
        """
        if not self.raw_path.exists():
            raise FileNotFoundError(
                f"Incident database file not found at expected location: {self.raw_path}"
            )

        # Header is at row index 2 (line 3 in Excel)
        raw_df = pd.read_excel(
            self.raw_path,
            sheet_name="Incident Database",
            header=2,
        )

        df = raw_df.rename(columns=self.COLUMN_MAPPING).copy()

        # String cleanup
        str_cols = ["plant", "tag_number", "eq_class", "discipline", "component", "ar_no"]
        for col in str_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.upper()

        # Numeric conversions
        num_cols = [
            "downtime_hrs",
            "actual_loss_k_usd",
            "potential_loss_k_usd",
            "total_loss_k_usd",
            "risk_score",
        ]
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        # Date normalization
        if "occur_date" in df.columns:
            df["occur_date"] = pd.to_datetime(df["occur_date"], errors="coerce").dt.strftime(
                "%Y-%m-%d"
            )

        # Sort chronologically
        df = df.sort_values(by=["occur_date", "serial_no"]).reset_index(drop=True)

        # Save to processed directory
        self.processed_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.processed_path, index=False, encoding="utf-8")

        return df

    def get_cleaned_df(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Retrieves cleansed incidents DataFrame from CSV cache, or reloads
        from raw Excel if cache is missing or force_reload is True.
        """
        if not force_reload and self.processed_path.exists():
            df = pd.read_csv(self.processed_path, encoding="utf-8")
            # Ensure types
            num_cols = [
                "downtime_hrs",
                "actual_loss_k_usd",
                "potential_loss_k_usd",
                "total_loss_k_usd",
                "risk_score",
            ]
            for col in num_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
            return df

        return self.load_and_clean()
