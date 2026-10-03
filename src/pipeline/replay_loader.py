"""
Data Ingestion & Single-Speed Replay Loader untuk POC Hackathon.
Membaca dataset timeseries dari data/extracted/ atau data/processed/.
"""

import os
import pandas as pd


class ReplayLoader:
    def __init__(self, data_path: str):
        self.data_path = data_path

    def load_dataset(self, filename: str) -> pd.DataFrame:
        target = os.path.join(self.data_path, filename)
        if not os.path.exists(target):
            raise FileNotFoundError(f"File {target} tidak ditemukan.")
        if target.endswith(".xlsx"):
            return pd.read_excel(target)
        elif target.endswith(".csv"):
            return pd.read_csv(target)
        raise ValueError("Format file tidak didukung (.csv atau .xlsx saja)")
