# Bug fix report: zero rolling window in `Volume_Bias`

## Summary

Master computes the short moving-average window as `n // 24`.

For small test periods such as `3, 5, 7, 10, 14, 20`, that expression evaluates to `0`. Pandas does not allow `rolling(0)`. `config-pandas` clamps the short window to at least `1`.

## Master failures

56-ticker validation on master produced:

- `Volume_Bias`: 336 failures

Error:

```text
min_periods 1 must be <= window 0
```

Why 336 rather than 560:

- the error only occurs for periods where `n // 24 == 0`
- that happens for 6 of the 10 tested periods
- `56 tickers * 6 periods = 336 failures`

## Master code

```python
df[factor_name] = (
    df['quote_volume'].rolling(n // 24, min_periods=1).mean()
    / df['quote_volume'].rolling(n, min_periods=1).mean()
    - 1
)
```

For `n = 3`:

```python
n // 24 = 0
```

So pandas receives `rolling(0, min_periods=1)`, which is invalid.

## `config-pandas` fix

```python
short_n = max(1, n // 24)
df[factor_name] = (
    df["quote_volume"].rolling(short_n, min_periods=config.min_periods).mean()
    / df["quote_volume"].rolling(n, min_periods=config.min_periods).mean()
    - 1
)
```

## Why this fix is correct

The formula wants a short-window moving average relative to the longer `n`-period average. A zero-length window has no mathematical meaning.

Clamping to `1` is the smallest valid rolling window and matches the intended behavior for very small `n`:

- if `n` is too small for `n/24` to reach one full period
- use the current bar as the shortest possible average

## Validation

- Master, 56 tickers: 336 failures for `Volume_Bias`
- `config-pandas`, 56 tickers: 0 failures for `Volume_Bias`

## Conclusion

This is a simple window-size bug in master.

The formula-derived short window can evaluate to zero for small `n`. `config-pandas` fixes that by clamping the short window with `max(1, n // 24)` before calling `rolling()`.
