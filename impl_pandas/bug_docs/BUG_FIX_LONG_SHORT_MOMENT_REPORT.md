# Bug fix report: `LongMoment` and `ShortMoment`

## Summary

Master computes these two indicators with `rolling(...).apply(...)` and a callback that uses the rolling window's pandas index labels to slice a numpy array.

That is fragile. It broke under the current runtime and produced 56-ticker failures for both indicators.

`config-pandas` replaces that callback-based approach with an explicit numpy loop over positional windows.

## Master failures

56-ticker validation on master produced:

- `LongMoment`: 560 failures
- `ShortMoment`: 560 failures

Error:

```text
only integers, slices (:), ellipsis (...), numpy.newaxis (None) and integer or boolean arrays are valid indices
```

Total fixed by this change: **1,120 status failures**.

## Root cause

Master defines a nested callback like this:

```python
def range_plus(x, np_tmp, rolling_window, lam):
    li = x.index.to_list()
    np_tmp2 = np_tmp[li, :]
```

`x` is a pandas rolling window. Its `.index` values are pandas index labels, not guaranteed numpy row positions. The callback then uses those labels to index a plain numpy array:

```python
np_tmp2 = np_tmp[li, :]
```

That only works if the labels happen to be valid integer positions. It breaks when pandas passes an index object that numpy does not accept as a positional selector.

## Master implementation

### `momentum_feature/LongMoment.py`

Master logic:

```python
np_tmp = df[['amplitude', 'price_change']].values
df[factor_name] = df['price_change'].rolling(n * 10).apply(
    range_plus, args=(np_tmp, n * 10, 0.7), raw=False
)
```

### `momentum_feature/ShortMoment.py`

Master logic:

```python
np_tmp = df[['amplitude', 'price_change']].values
df[factor_name] = df['price_change'].rolling(n).apply(
    range_plus, args=(np_tmp, n, 0.7), raw=False
)
```

Both use the same indexing pattern.

## Fix in `config-pandas`

`config-pandas` rewrites both indicators as direct positional loops.

### `LongMoment`

```python
window = n * 10
result = np.full(len(df), np.nan)
for i in range(window - 1, len(df)):
    block = np.column_stack([np_amp[i - window + 1 : i + 1], np_pc[i - window + 1 : i + 1]])
    block = block[np.argsort(block[:, 0])]
    t = int(window * 0.7)
    result[i] = block[:t, 1].sum()
df[factor_name] = result
```

### `ShortMoment`

Same structure, with `window = n`.

## Why this fix is correct

The formula only needs positional rolling windows:

1. take the last `window` rows
2. sort them by amplitude
3. keep the lowest 70%
4. sum their price changes

No label-based indexing is part of the formula. The explicit positional loop matches the intended computation and removes the pandas-to-numpy indexing ambiguity.

## Side effects

The fixed version also improves readability:

- no nested callback
- no dependence on pandas rolling `apply`
- no hidden reliance on `.index`
- easier to compare with the formula in the comment

## Validation

- Master, 56 tickers: 1,120 failures across `LongMoment` and `ShortMoment`
- `config-pandas`, 56 tickers: 0 failures across both indicators

## Conclusion

This is a real implementation bug in master.

The old code mixed pandas label indexing with numpy positional indexing inside a rolling callback. `config-pandas` fixes it by computing the rolling window explicitly with positional slices.
