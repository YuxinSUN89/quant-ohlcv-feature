# Bug fix report: dtype-sensitive assignment in `Bolling` and `PriceVolumeResist`

## Summary

Master creates helper columns with integer dtype and later writes floating-point values or `np.inf` into them.

That worked loosely in older environments. Under the current pandas runtime, those assignments fail. `config-pandas` fixes the issue by initializing the helper columns as floats before writing float values.

## Master failures

56-ticker validation on master produced:

- `Bolling`: 560 failures
- `PriceVolumeResist`: 560 failures

Errors:

```text
Bolling: Invalid value '[...]' ...
PriceVolumeResist: Invalid value 'inf' for dtype 'int64'
```

Total fixed by this change: **1,120 status failures**.

## Case 1: `volatility_feature/Bolling.py`

### Master code

```python
df['distance'] = 0
...
df.loc[condition_1, 'distance'] = df['close'] - df['upper']
df.loc[condition_2, 'distance'] = df['close'] - df['lower']
```

`df['distance'] = 0` creates an integer column.

Later, pandas tries to assign floating-point arrays into that integer column. That fails under stricter dtype handling.

### `config-pandas` fix

```python
df["distance"] = 0.0
```

That creates a float column up front. The subsequent assignments match the column dtype.

## Case 2: `composite_feature/PriceVolumeResist.py`

### Master code

```python
df["direction"] = 1
df["adj"] = 1
...
df.loc[condition, 'adj'] = np.inf
```

`direction` and `adj` start as integer columns. Then master writes `np.inf` into `adj`. Pandas rejects that because `np.inf` does not fit an integer dtype.

### `config-pandas` fix

```python
df["direction"] = 1.0
df["adj"] = 1.0
```

That makes both helper columns float-typed before any conditional writes.

## Why this fix is correct

The indicator formulas already treat these helper columns as numeric intermediates, not integer counters.

- `distance` stores price differences, which are floats
- `direction` and `adj` participate in floating-point arithmetic
- `adj` explicitly needs to hold `np.inf`

So float initialization matches the actual data domain.

## Validation

- Master, 56 tickers: 1,120 failures across these two indicators
- `config-pandas`, 56 tickers: 0 failures across these two indicators

## Conclusion

This is a dtype initialization bug in master.

The old code created integer helper columns and later assigned float values into them. `config-pandas` fixes the problem by initializing those helper columns with floating-point literals.
