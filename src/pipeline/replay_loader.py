"""
Replay Loader & Data Ingestion Pipeline for SCC-Caliber.
Implements 3-layer cleansing, smart caching, and streaming replay generator
for continuous petrochemical timeseries data (ZCU Cracker Unit equipment).
"""

from pathlib import Path
import time
from typing import Any, Dict, Iterator, Optional, Tuple, Union

import numpy as np
import openpyxl
import pandas as pd


class ReplayLoader:
    """
    Timeseries data loader and stream generator for petrochemical equipment sensors.
    
    Attributes:
        equipment_tag (str): Equipment identifier (e.g., 'KO-3201', 'PU-2101B').
        data_dir (Path): Directory containing raw production Excel files.
        processed_dir (Path): Directory for cached, cleansed CSV files.
        frozen_tag_report (dict): Summary of detected frozen sensor tags.
    """

    def __init__(
        self,
        equipment_tag: str = "KO-3201",
        data_dir: Optional[Union[str, Path]] = None,
        processed_dir: Optional[Union[str, Path]] = None,
    ):
        self.equipment_tag = equipment_tag.strip().upper()
        self.clean_tag = self.equipment_tag.replace("-", "")

        # Default paths relative to project root
        project_root = Path(__file__).resolve().parents[2]
        if data_dir is None:
            self.data_dir = (
                project_root
                / "data"
                / "extracted"
                / "Supporting Data"
                / "Case 2_ Intelligence Manufacturing"
                / "Production Data"
            )
        else:
            self.data_dir = Path(data_dir)

        if processed_dir is None:
            self.processed_dir = project_root / "data" / "processed"
        else:
            self.processed_dir = Path(processed_dir)

        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.raw_file_path = self._locate_raw_file()
        self.metadata: Optional[pd.DataFrame] = None
        self.frozen_tag_report: Dict[str, Any] = {}

    def _locate_raw_file(self) -> Path:
        """Locates the raw production Excel file matching the equipment tag."""
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

        candidates = list(self.data_dir.glob("*.xlsx"))
        for candidate in candidates:
            # Check exact match or normalized tag in filename
            name_upper = candidate.name.upper()
            if self.equipment_tag in name_upper or self.clean_tag in name_upper:
                return candidate

        raise FileNotFoundError(
            f"No production Excel file found for equipment '{self.equipment_tag}' in {self.data_dir}"
        )

    def load_metadata(self) -> pd.DataFrame:
        """
        Reads instrument metadata from the 'PI Tag' sheet.
        
        Returns:
            pd.DataFrame: Tag specifications including engunits, span, and zero.
        """
        try:
            meta_df = pd.read_excel(self.raw_file_path, sheet_name="PI Tag")
            self.metadata = meta_df
            return meta_df
        except Exception as e:
            raise ValueError(f"Failed to read 'PI Tag' sheet from {self.raw_file_path}: {e}")

    def clean_and_align(
        self,
        df: pd.DataFrame,
        metadata: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        """
        Executes 3-layer cleansing and feature alignment:
        - Layer 1: Physical Span Filtering (eliminate negative physical values)
        - Layer 2: Imputation & Frozen Tag Detection (ffill + frozen tag check >4h)
        - Layer 3: Binary Status Normalization & First-Order Time Derivatives (dx/dt)
        
        Args:
            df (pd.DataFrame): Raw telemetry timeseries.
            metadata (Optional[pd.DataFrame]): PI Tag instrument specifications.
            
        Returns:
            pd.DataFrame: Cleaned and feature-augmented timeseries dataframe.
        """
        cleaned = df.copy()

        # Ensure Timestamp is parsed and sorted chronologically
        if "Timestamp" not in cleaned.columns:
            raise KeyError("Column 'Timestamp' is missing from input data.")
        cleaned["Timestamp"] = pd.to_datetime(cleaned["Timestamp"])
        cleaned = cleaned.sort_values("Timestamp").reset_index(drop=True)

        # Layer 3 prep: Normalize RUN_STATUS early for conditional checks
        if "RUN_STATUS" in cleaned.columns:
            cleaned["RUN_STATUS"] = (
                cleaned["RUN_STATUS"]
                .astype(str)
                .str.strip()
                .str.upper()
                .map({"ON": 1, "1": 1, "TRUE": 1, "OFF": 0, "0": 0, "FALSE": 0})
                .fillna(0)
                .astype("int64")
            )

        # Identify numeric process sensor columns
        non_process_cols = {"Timestamp", "RUN_STATUS"}
        sensor_cols = [c for c in cleaned.columns if c not in non_process_cols]

        # Layer 1: Physical Span Filter (Rejection of negative values for physical parameters)
        for col in sensor_cols:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
            # Vibration, temperature, pressure, feed flow, and current cannot be negative
            neg_mask = cleaned[col] < 0.0
            if neg_mask.any():
                cleaned.loc[neg_mask, col] = np.nan

        # Layer 2: Missing Imputation (Forward-fill, then backward-fill for leading nulls)
        cleaned[sensor_cols] = cleaned[sensor_cols].ffill().bfill()

        # Layer 2: Frozen Tag Detection (> 4 consecutive hours constant while running)
        self.frozen_tag_report = {}
        is_running = cleaned.get("RUN_STATUS", pd.Series(1, index=cleaned.index)) == 1

        for col in sensor_cols:
            series = cleaned[col]
            is_same = series == series.shift(1)
            # Group consecutive identical values
            consecutive_counts = is_same.groupby((~is_same).cumsum()).cumsum()
            frozen_mask = (consecutive_counts >= 4) & is_running
            frozen_instances = int(frozen_mask.sum())
            if frozen_instances > 0:
                self.frozen_tag_report[col] = {
                    "frozen_points_count": frozen_instances,
                    "first_frozen_timestamp": str(cleaned.loc[frozen_mask, "Timestamp"].iloc[0]),
                }

        # Layer 3: Feature Augmentation - First-Order Time Derivative (dx/dt)
        for col in sensor_cols:
            cleaned[f"d_{col}"] = cleaned[col].diff().fillna(0.0)

        return cleaned

    def get_data(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Loads cleaned timeseries data with smart local caching.
        
        Args:
            force_reload (bool): If True, re-parses Excel and overwrites CSV cache.
            
        Returns:
            pd.DataFrame: Cleaned timeseries ready for analysis or UI.
        """
        cache_path = self.processed_dir / f"{self.clean_tag}_cleaned.csv"

        if cache_path.exists() and not force_reload:
            cached_df = pd.read_csv(cache_path, parse_dates=["Timestamp"])
            return cached_df

        # Load raw Excel data
        metadata = self.load_metadata()
        wb = openpyxl.load_workbook(self.raw_file_path, read_only=True)
        sheet_names = wb.sheetnames
        data_sheet = "Sheet2" if "Sheet2" in sheet_names else [s for s in sheet_names if s != "PI Tag"][0]

        raw_df = pd.read_excel(self.raw_file_path, sheet_name=data_sheet)
        cleaned_df = self.clean_and_align(raw_df, metadata=metadata)

        # Write to local cache
        cleaned_df.to_csv(cache_path, index=False)
        return cleaned_df

    def stream(
        self, window_size: int = 24, delay: float = 0.0
    ) -> Iterator[Tuple[pd.Series, pd.DataFrame]]:
        """
        Yields sequential timeseries stream with a sliding window buffer.
        
        Args:
            window_size (int): Number of historical hours included in buffer.
            delay (float): Optional simulated interval between iterations in seconds.
            
        Yields:
            Tuple[pd.Series, pd.DataFrame]: Current telemetry point and historical window.
        """
        df = self.get_data()
        n_rows = len(df)

        for i in range(n_rows):
            current_row = df.iloc[i]
            start_idx = max(0, i - window_size + 1)
            history_window = df.iloc[start_idx : i + 1]
            yield current_row, history_window
            if delay > 0.0:
                time.sleep(delay)
