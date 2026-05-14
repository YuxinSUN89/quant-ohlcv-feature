"""Runtime configuration for indicator DataFrame operations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class IndicatorConfig:
    """Numerical defaults used by all indicators.

    ``min_periods=None`` means use the backend's strict rolling default.
    For an integer window this is equivalent to ``min_periods=window`` in
    pandas and to ``min_samples=window`` in polars.
    """

    min_periods: Optional[int] = None
    ddof: int = 1
    ewm_adjust: bool = True
    eps: float = 1e-8
    normalize_eps: float = 1e-9
    strict_columns: bool = False
    fill_method: Optional[str] = None
    use_numba: bool = True
    backend: str = "auto"

    def snapshot(self) -> dict[str, Any]:
        """JSON-serializable representation for test result headers."""
        return asdict(self)


def unwrap_configured(obj: Any) -> Any:
    """Return the underlying pandas/polars object (no-op — proxies removed)."""
    return obj


def ensure_columns(df: Any, config: IndicatorConfig) -> Any:
    """Add zero-filled columns for any missing columns referenced by indicators."""
    extra_cols = ["trade_num", "taker_buy_base_asset_volume"]
    try:
        import pandas as pd

        if isinstance(df, pd.DataFrame):
            for col in extra_cols:
                if col not in df.columns:
                    df = df.copy()
                    df[col] = 0.0
            return df
    except ImportError:
        pass
    try:
        import polars as pl

        if isinstance(df, pl.DataFrame):
            existing = set(df.columns)
            for col in extra_cols:
                if col not in existing:
                    df = df.with_columns(pl.Series(col, [0.0] * len(df)))
    except ImportError:
        pass
    return df
