"""Path-resolution logic for the Manual Matching launcher.

Kept separate from the Tkinter UI so it can be unit tested without a display.
"""

from __future__ import annotations

import re
from pathlib import Path

ENGINES = [
    "AutoCopy",
    "Oracle Cash",
    "Manual Journal",
    "Monthly Journal",
    "Spreadsheet",
    "Oracle Payables",
    "Oracle Receivables",
    "SAP",
]

PERIOD_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


class InvalidPeriodError(ValueError):
    pass


def default_base_dir() -> Path:
    """The ReconcilePro periods root under the current user's own profile."""
    return Path.home() / "Documents" / "ReconcilePro" / "operating_files" / "periods"


def validate_period(period: str) -> str:
    period = period.strip()
    if not PERIOD_PATTERN.match(period):
        raise InvalidPeriodError(f"Date period must be in YYYY-MM format, got {period!r}")
    return period


def resolve_source_path(engine: str, period: str, base_dir: Path | None = None) -> Path:
    """Build the expected source-file path for an engine/period combination.

    {base_dir}\\{YYYY-MM}\\raw\\Manual Matching\\{Engine}_{YYYY-MM}-MM.xlsx
    """
    engine = engine.strip()
    if not engine:
        raise ValueError("Engine must not be empty")
    period = validate_period(period)
    base_dir = base_dir if base_dir is not None else default_base_dir()

    filename = f"{engine}_{period}-MM.xlsx"
    return base_dir / period / "raw" / "Manual Matching" / filename


def recent_periods(count_back: int = 24, count_forward: int = 2, today=None) -> list[str]:
    """Generate a list of YYYY-MM strings for the dropdown, most recent first."""
    from datetime import date

    today = today or date.today()
    year, month = today.year, today.month

    periods = []
    total = count_back + count_forward + 1
    # start `count_forward` months ahead of today, walk backwards
    y, m = year, month
    for _ in range(count_forward):
        m += 1
        if m > 12:
            m = 1
            y += 1
    for _ in range(total):
        periods.append(f"{y:04d}-{m:02d}")
        m -= 1
        if m < 1:
            m = 12
            y -= 1
    return periods
