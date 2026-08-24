from datetime import date
from pathlib import Path

import pytest

from path_resolver import (
    InvalidPeriodError,
    recent_periods,
    resolve_source_path,
    validate_period,
)


def test_resolve_source_path_matches_work_order_example():
    base = Path(r"C:\Users\swalk\Documents\ReconcilePro\operating_files\periods")
    result = resolve_source_path("Spreadsheet", "2025-09", base_dir=base)
    expected = base / "2025-09" / "raw" / "Manual Matching" / "Spreadsheet_2025-09-MM.xlsx"
    assert result == expected


def test_resolve_source_path_matches_original_sap_example():
    base = Path(r"C:\Users\swalk\Documents\ReconcilePro\operating_files\periods")
    result = resolve_source_path("SAP", "2025-12", base_dir=base)
    expected = base / "2025-12" / "raw" / "Manual Matching" / "SAP_2025-12-MM.xlsx"
    assert result == expected


def test_invalid_period_raises():
    with pytest.raises(InvalidPeriodError):
        validate_period("2025-13")
    with pytest.raises(InvalidPeriodError):
        validate_period("2025-9")
    with pytest.raises(InvalidPeriodError):
        validate_period("09-2025")


def test_valid_period_passes_through():
    assert validate_period(" 2025-09 ") == "2025-09"


def test_recent_periods_includes_current_and_future_months():
    periods = recent_periods(count_back=2, count_forward=1, today=date(2025, 9, 15))
    assert periods == ["2025-10", "2025-09", "2025-08", "2025-07"]
