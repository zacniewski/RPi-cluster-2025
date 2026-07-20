"""
validate.py — Data validation engine for pawn-cluster.

Reads validation rules from a YAML config and checks a pandas DataFrame
against them. Returns (passed: bool, report: str).

Checks performed:
  1. Required columns exist
  2. Column dtypes match expectations
  3. Values fall within specified ranges
  4. Missing-value percentage is below threshold
  5. Minimum row count is met
"""

from __future__ import annotations

import pandas as pd


def validate_dataframe(df: pd.DataFrame, rules: dict) -> tuple[bool, str]:
    """Validate a DataFrame against the given rules dict.

    Returns:
        (True, "All checks passed") on success, or
        (False, "...details...") on failure.
    """
    errors: list[str] = []

    # 1. Required columns
    required = rules.get("required_columns", [])
    missing_cols = [c for c in required if c not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")

    # 2. Column types
    expected_types = rules.get("column_types", {})
    for col, expected in expected_types.items():
        if col in df.columns:
            actual = str(df[col].dtype)
            if actual != expected:
                # Try casting — if it works, accept it
                try:
                    df[col] = df[col].astype(expected)
                except (ValueError, TypeError):
                    errors.append(
                        f"Column '{col}' has dtype '{actual}', expected '{expected}'"
                    )

    # 3. Range checks
    range_checks = rules.get("range_checks", {})
    for col, bounds in range_checks.items():
        if col not in df.columns:
            continue
        col_min = df[col].min()
        col_max = df[col].max()
        if "min" in bounds and col_min < bounds["min"]:
            errors.append(
                f"Column '{col}' min value {col_min} is below allowed {bounds['min']}"
            )
        if "max" in bounds and col_max > bounds["max"]:
            errors.append(
                f"Column '{col}' max value {col_max} is above allowed {bounds['max']}"
            )

    # 4. Missing values
    max_missing_pct = rules.get("max_missing_pct", 100.0)
    for col in df.columns:
        pct = df[col].isna().mean() * 100
        if pct > max_missing_pct:
            errors.append(
                f"Column '{col}' has {pct:.1f}% missing values (max allowed: {max_missing_pct}%)"
            )

    # 5. Minimum rows
    min_rows = rules.get("min_rows", 0)
    if len(df) < min_rows:
        errors.append(f"Dataset has {len(df)} rows, minimum required is {min_rows}")

    if errors:
        return False, "\n".join(errors)
    return True, "All checks passed"
