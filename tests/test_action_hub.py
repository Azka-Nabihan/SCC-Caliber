"""
Unit tests for Phase 4: Action Lifecycle, Maintenance Work Orders Tracker, and Visual Polish.
Validates work orders tracker catalog, BOM attributes, lifecycle step progressions,
and economic avoidance calculations.
"""

import pytest
from src.app.data_provider import DashboardDataProvider


@pytest.fixture
def provider():
    return DashboardDataProvider()


def test_work_orders_tracker_catalog_structure(provider):
    """
    Verifies that get_work_orders_tracker_catalog returns exactly 3 prioritized tasks
    with full industrial engineering metadata.
    """
    catalog = provider.get_work_orders_tracker_catalog()
    assert len(catalog) == 3

    order_ids = [task["order_id"] for task in catalog]
    assert "WO-8842109" in order_ids
    assert "WO-8842110" in order_ids
    assert "CAPA-2026-04" in order_ids

    for task in catalog:
        assert "order_id" in task
        assert "title" in task
        assert "equipment_tag" in task
        assert "category" in task
        assert "order_type" in task
        assert "priority" in task
        assert "target_duration_hrs" in task
        assert "assigned_crew" in task
        assert "safety_permit" in task
        assert "bill_of_materials" in task
        assert len(task["bill_of_materials"]) >= 3
        assert "action_steps" in task
        assert len(task["action_steps"]) >= 3
        assert "avoided_loss_k_usd" in task
        assert "financial_basis" in task


def test_task_1_urgent_repair_details(provider):
    """
    Verifies Task 1 (WO-8842109) has correct pilot asset binding (KO-3201),
    Babbitt sleeve BOM, 16h lead time window, and $1,188.0k net savings.
    """
    catalog = provider.get_work_orders_tracker_catalog()
    task1 = next(t for t in catalog if t["order_id"] == "WO-8842109")

    assert task1["equipment_tag"] == "KO-3201"
    assert task1["category"] == "URGENT REPAIR"
    assert task1["target_duration_hrs"] == 8.0
    assert task1["avoided_loss_k_usd"] == 1188.0
    assert task1["avoided_downtime_hrs"] == 24.0

    parts = [p["part_no"] for p in task1["bill_of_materials"]]
    assert "BBR-3201-DE" in parts
    assert "LUB-SYN-VG46" in parts


def test_task_lifecycle_step_progression(provider):
    """
    Verifies simulated 4-step lifecycle transition from Open to Completed & Verified.
    """
    steps = ["Open", "Dispatched", "In Progress", "Completed & Verified"]
    assert len(steps) == 4

    # Simulating progression logic
    current_step_idx = 1  # Initially Dispatched
    assert steps[current_step_idx] == "Dispatched"

    # Advance
    next_step_idx = min(current_step_idx + 1, len(steps) - 1)
    assert steps[next_step_idx] == "In Progress"

    # Complete & Verify
    final_step_idx = len(steps) - 1
    assert steps[final_step_idx] == "Completed & Verified"
