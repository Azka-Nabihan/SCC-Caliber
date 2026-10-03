"""
Unit Tests for ReplayLoader Data Pipeline (SCC-Caliber Phase 1).
Validates metadata reading, 3-layer cleansing, smart caching, and stream generator.
"""

from pathlib import Path
import shutil
import pytest
import pandas as pd
import numpy as np

from src.pipeline.replay_loader import ReplayLoader


@pytest.fixture
def loader():
    """Provides a ReplayLoader instance pointing to KO-3201 raw telemetry."""
    return ReplayLoader(equipment_tag="KO-3201")


def test_load_raw_and_metadata(loader):
    """Verifies that the raw Excel file exists and 'PI Tag' metadata is parsed."""
    assert loader.raw_file_path.exists(), f"Raw file does not exist: {loader.raw_file_path}"
    
    metadata = loader.load_metadata()
    assert isinstance(metadata, pd.DataFrame)
    assert not metadata.empty
    assert "Name" in metadata.columns
    assert "engunits" in metadata.columns
    assert len(metadata) >= 5, "Metadata should contain at least 5 instrument tags"


def test_3_layer_cleansing(loader):
    """
    Tests the 3-layer cleansing engine:
    - Layer 1: Physical span filter (no negative sensor values)
    - Layer 2: Imputation & frozen tag detection
    - Layer 3: Binary RUN_STATUS & time derivatives (dx/dt)
    """
    # Create synthetic test dataset with intentional flaws
    timestamps = pd.date_range("2026-04-01", periods=10, freq="1h")
    dirty_data = pd.DataFrame({
        "Timestamp": timestamps,
        "KO3201_VIB": [1.2, -0.5, 1.4, 2.0, 2.0, 2.0, 2.0, 2.0, 2.1, 2.2],  # Negative value + frozen segment
        "KO3201_TEMP": [65.0, 65.5, np.nan, 66.0, 66.2, 66.5, 67.0, 67.2, 67.5, 68.0],  # NaN value
        "RUN_STATUS": ["ON", "ON", "ON", "ON", "ON", "ON", "ON", "ON", "OFF", "OFF"]
    })

    cleaned = loader.clean_and_align(dirty_data)

    # Layer 1 assertions
    assert pd.api.types.is_datetime64_any_dtype(cleaned["Timestamp"])
    assert (cleaned["KO3201_VIB"] >= 0.0).all(), "Negative vibration values must be eliminated"

    # Layer 2 assertions
    assert cleaned["KO3201_TEMP"].isna().sum() == 0, "Missing values must be imputed"
    assert "KO3201_VIB" in loader.frozen_tag_report, "Sensor KO3201_VIB should be flagged as frozen"
    assert loader.frozen_tag_report["KO3201_VIB"]["frozen_points_count"] >= 1

    # Layer 3 assertions
    assert set(cleaned["RUN_STATUS"].unique()).issubset({0, 1}), "RUN_STATUS must be binary integers"
    assert "d_KO3201_VIB" in cleaned.columns, "Time derivative column must be generated"
    assert "d_KO3201_TEMP" in cleaned.columns


def test_smart_caching(loader, tmp_path):
    """Verifies that data is parsed, saved to CSV cache, and reloaded accurately."""
    # Use temporary processed directory to isolate caching test
    custom_processed = tmp_path / "processed"
    custom_loader = ReplayLoader(equipment_tag="KO-3201", processed_dir=custom_processed)
    
    expected_cache = custom_processed / "KO3201_cleaned.csv"
    assert not expected_cache.exists(), "Cache should not exist before execution"

    # First call: Processes Excel and creates cache
    df1 = custom_loader.get_data(force_reload=False)
    assert expected_cache.exists(), "Cache file must be created"
    assert len(df1) == 720, f"Expected 720 hourly records, got {len(df1)}"

    # Second call: Reads directly from CSV cache
    df2 = custom_loader.get_data(force_reload=False)
    pd.testing.assert_frame_equal(df1, df2)


def test_stream_generator(loader):
    """Verifies that the generator yields consecutive sliding windows correctly."""
    df = loader.get_data()
    window_size = 24
    stream = loader.stream(window_size=window_size)

    # Step 1: Initial window
    curr_0, window_0 = next(stream)
    assert curr_0["Timestamp"] == df.iloc[0]["Timestamp"]
    assert len(window_0) == 1, "First window should have size 1 at index 0"

    # Step 25: Sliding window should reach full capacity of 24
    curr_24 = None
    window_24 = None
    for _ in range(24):
        curr_24, window_24 = next(stream)

    assert len(window_24) == window_size, f"Window at index 24 should have size {window_size}"
    assert window_24.iloc[-1]["Timestamp"] == curr_24["Timestamp"], "Last element in window must match current row"
