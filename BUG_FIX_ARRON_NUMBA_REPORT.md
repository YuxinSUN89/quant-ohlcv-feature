# Bug fix report: `Arron` numba signature mismatch

## Summary

Master calls a numba-compiled helper with argument dtypes that do not match the compiled signature.

That causes every `Arron` run to fail under the current runtime. `config-pandas` fixes the call by casting both arguments to the exact dtypes numba expects.

## Master failures

56-ticker validation on master produced:

- `Arron`: 560 failures

Error:

```text
No matching definition for argument type(s) readonly array(float64, 1d, C), int64
```

Total fixed by this change: **560 status failures**.

## Root cause

Master defines this helper:

```python
@nb.njit(nb.int32[:](nb.float64[:], nb.int32), cache=True)
def rolling_argmin_queue(arr, n):
    ...
```

That signature is strict:

- first argument: `float64[:]`
- second argument: `int32`

Master then calls it like this:

```python
low_len = rolling_argmin_queue(df['low'].values, n)
high_len = rolling_argmin_queue(-df['high'].values, n)
```

At runtime, pandas supplies an array that numba sees as a readonly float array, and `n` arrives as `int64`. That does not match the compiled signature.

## Fix in `config-pandas`

`config-pandas` casts both inputs explicitly:

```python
low_len = rolling_argmin_queue(np.array(df["low"].values, dtype=np.float64), np.int32(n))
high_len = rolling_argmin_queue(np.array(-df["high"].values, dtype=np.float64), np.int32(n))
```

That makes the call match the declared numba signature exactly.

## Why this fix is correct

The numba function already declares the intended ABI. The bug is not in the algorithm. The bug is in the call site.

`config-pandas` does not change the queue logic. It only makes the runtime dtypes agree with the compiled signature.

## Secondary cleanup

`config-pandas` also moved the shared z-score helper into `helpers.py` and uses:

```python
df[factor_name] = scale_zscore(s, n, config=config)
```

That cleanup is independent of the numba fix. The status failure comes from the dtype mismatch.

## Validation

- Master, 56 tickers: 560 failures for `Arron`
- `config-pandas`, 56 tickers: 0 failures for `Arron`

## Conclusion

This is a runtime dtype bug in master.

The compiled numba helper expects `float64[:]` and `int32`. Master passed values that did not meet that signature. `config-pandas` fixes the problem with explicit casting at the call site.
