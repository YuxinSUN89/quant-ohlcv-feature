# AGENTS.md — Coding Conventions for Indicator Development

This file documents the numerical and API patterns that must be followed when writing or modifying indicator files. All 335+ indicators live under `impl_pandas/` and `impl_polars/` and share a uniform `signal(df, n, factor_name, config)` signature.

## Config-Driven Numerical Defaults

All numerical parameters come from `IndicatorConfig` (defined in `indicator_config.py`). **Never hardcode numerical constants.**

```python
@dataclass(frozen=True)
class IndicatorConfig:
    min_periods: Optional[int] = None   # rolling window min_periods / min_samples
    ddof: int = 1                       # delta degrees of freedom for std
    ewm_adjust: bool = True             # ewm adjust parameter
    eps: float = 1e-8                   # division-by-zero floor
    normalize_eps: float = 1e-9         # normalization / comparison epsilon
```

### Which epsilon to use

| Constant | Field | When to use |
|---|---|---|
| Division-by-zero guard | `config.eps` (1e-8) | Denominators in `/ col`, `/ rolling_std()`, `/ rolling_sum()` |
| Normalization / comparison threshold | `config.normalize_eps` (1e-9) | `np.where(np.abs(prev) > eps, ...)`, boundary comparisons |

## Numerical Safety Rules

### 1. Protect every computed denominator with `+ config.eps`

Any division by a column that is not raw OHLCV (i.e. a rolling stat, a shifted value, or an intermediate calculation) **must** add `config.eps` to the denominator.

```python
# ✗ WRONG — division by zero when std = 0 (flat price window)
df["grid"] = (df["close"] - df["median"]) / df["std"]

# ✓ CORRECT
df["grid"] = (df["close"] - df["median"]) / (df["std"] + config.eps)
```

This applies to all of these patterns:

| Denominator type | Example | Risk |
|---|---|---|
| Rolling std | `df["close"].rolling(n).std()` | Zero when price is flat for N bars |
| Rolling sum of volume/TR | `df["TR_sum"]`, `df["vma"]` | Zero for illiquid assets or first N bars |
| Shifted price/volume | `df["close"].shift(n)` | Zero if bar has zero close |
| Rolling mean (as denominator) | `df["sma"]`, `df["ma"]` | Zero for delisted assets |
| Intermediate computed range | `df["max_high"] - df["min_low"]` | Zero when high==low for N bars |
| Computed ratio | `df["volume_ratio"]`, `df["R"]` | Zero from degenerate inputs |

### 2. Rolling range denominators must use both bounds

When computing price position within a rolling range, the denominator is `(max - min)`, not `(max - current)`.

```python
# ✗ WRONG — uses current low instead of rolling min
df["price_ch"] = 2 * (df["price"] - df["min_low"]) / (df["max_high"] - df["low"]) - 0.5

# ✓ CORRECT — full rolling range with eps guard
df["price_ch"] = 2 * (df["price"] - df["min_low"]) / (df["max_high"] - df["min_low"] + config.eps) - 0.5
```

### 3. Use `config.normalize_eps` for pct_change denominator guards

When implementing custom pct_change with a denominator floor:

```python
# ✗ WRONG — hardcoded epsilon
df[factor_name] = (grid_arr - prev) / np.where(np.abs(prev) > 1e-9, prev, np.nan)

# ✓ CORRECT — config-driven
df[factor_name] = (grid_arr - prev) / np.where(np.abs(prev) > config.normalize_eps, prev, np.nan)
```

### 4. Never use `inplace=True` on pandas operations

In-place mutations on DataFrame columns can corrupt the caller's data.

```python
# ✗ WRONG — mutates caller's Series
ser.fillna(value=0, inplace=True)
df["col"].fillna(value=0, inplace=True)

# ✓ CORRECT — returns new object
ser = ser.fillna(value=0)
df["col"] = df["col"].fillna(0)
```

Exception: `df.drop(columns=[...], inplace=True)` on local DataFrames is acceptable when the DataFrame is not shared with callers. However, the assignment form is preferred for clarity:

```python
# Preferred:
df = df.drop(columns=[...])       # pandas
df = df.drop(["col1", "col2"])    # polars
```

### 5. Use closed-form OLS instead of sklearn for rolling regression

Never import `sklearn.linear_model.LinearRegression` inside indicator files. It allocates an object per rolling window, triggers SVD, and can fail to converge on short windows.

```python
# ✗ WRONG — sklearn per row, SVD can fail
from sklearn.linear_model import LinearRegression
model = LinearRegression().fit(x.reshape(-1, 1), y)

# ✓ CORRECT — closed-form OLS, O(N) per window, no external deps
x = np.arange(m, dtype=float)
x_mean = (m - 1) / 2.0
y_mean = y_arr.mean()
slope = np.dot(x - x_mean, y_arr - y_mean) / (np.dot(x - x_mean, x - x_mean) + eps)
intercept = y_mean - slope * x_mean
return slope * (m - 1) + intercept
```

### 6. Use identical algorithms in both impls for cross-impl numerical match

When optimizing a computation (e.g. replacing a while loop), apply the **same algorithm** in both `impl_pandas/` and `impl_polars/`. Different algorithms (e.g. `rolling().rank()` in pandas vs numpy loop in polars) produce different numerics and defeat the cross-impl comparison test.

```python
# Both impls should use the same numpy loop:
pmar_np = df["pmar"].to_numpy()
result = np.full(len(pmar_np), np.nan)
for i in range(min_periods - 1, len(pmar_np)):
    window = pmar_np[max(0, i - n) : i + 1]
    result[i] = np.sum(window < pmar_np[i]) / n * 100
```

## Rolling Window Configuration

Always pass config parameters to rolling/EWM calls:

```python
# pandas
df["col"].rolling(n, min_periods=config.min_periods)
df["col"].std(ddof=config.ddof)
df["col"].ewm(span=n, adjust=config.ewm_adjust)

# polars
df["col"].rolling_min(n, min_samples=config.min_periods)
df["col"].rolling_std(n, min_samples=config.min_periods, ddof=config.ddof)
```

## Polars-Specific Rules

- Use `fill_nan(None)` to convert float NaN → polars null (so aggregations skip them, matching pandas behavior).
- Use `fill_null(0)` only when intentional (early zero-fill before division is dangerous — prefer `fill_nan(None)`).
- `np.where()` on polars Series produces NaN (not null); always chain `.fill_nan(None)`.

## File Structure

Every indicator file must:
- Export a single `signal(df, n, factor_name, config)` function.
- Delete all intermediate columns before returning `df`.
- Have a docstring with the formula in pseudo-math notation.
- Have an identical counterpart in the other impl with the same algorithm.

## Testing

```bash
python tests/run_suite_parallel.py --impl pandas   # 187,600 test cases
python tests/run_suite_parallel.py --impl polars    # 187,600 test cases
python tests/compare.py <pandas.csv> <polars.csv>   # cross-impl comparison
```

Both impls must pass 187,600/187,600 with zero failures. Cross-impl numerical match target: ≥99.8%.

## Known Remaining Floating-Point Diffs

As of `fix-review-issues` branch, 361/187,600 cases (0.19%) show small FP differences between pandas and polars in these indicators:
- `ZfAbsMean` (293 diffs, max_rel 1.4e-3) — recursive EMA accumulation
- `Stc` (17 diffs), `Acs` (10 diffs) — TA-Lib FP boundary
- `LongMoment`/`ShortMoment` (12 diffs) — higher-moment statistics
- `Grid` (3 diffs), `Qstick` (4 diffs) — inf from zero denominators in edge cases

These are acceptable FP-level differences and do not indicate logic errors.
