# Bug fix report: `ewm(n)` to `ewm(span=n)`

## Summary

Pandas treats the first positional argument of `Series.ewm()` as `com`, not `span`.

```python
Series.ewm(com=None, span=None, halflife=None, alpha=None, ...)
```

That means:

- `ewm(n)` means `ewm(com=n)`
- `ewm(span=n)` means an `n` period EMA

For an `n` period EMA, finance formulas use:

- `alpha = 2 / (n + 1)`
- `span = n`

`ewm(com=n)` uses:

- `alpha = 1 / (n + 1)`

So the positional form smooths much more slowly. It behaves more like a span of about `2n + 1`.

## Why this needed a fix

The affected indicators document formulas such as `EMA(CLOSE, N)`, `EMA(VOLUME, N1)`, `EMA(EMA(CLOSE, N), N)`, or similar. Those formulas mean a standard `N` period EMA. In pandas, that maps to `ewm(span=N)`, not `ewm(N)`.

The old code silently computed a different filter.

## Validation

I checked three things.

### 1. Pandas API semantics

`inspect.signature(pd.Series.ewm)` shows:

```python
(self, com=None, span=None, halflife=None, alpha=None, ...)
```

The first positional argument is `com`.

### 2. Indicator formulas

Each affected file documents an EMA formula in its comment or docstring. Examples:

- `PO`: `EMA_SHORT=EMA(CLOSE,N)`
- `TEMA`: `TEMA=3*EMA(CLOSE,N)-3*EMA(EMA(CLOSE,N),N)+EMA(EMA(EMA(CLOSE,N),N),N)`
- `MtmTb`: `MTM_MEAN = EMA(CLOSE/REF(CLOSE,N)-1, N)`
- `MACDVOL`: `EMA(VOLUME,N1)-EMA(VOLUME,N2)`

Those formulas call for `span=N`.

### 3. Real-data checks on AAPL

I compared three versions:

- reference EMA using `alpha = 2 / (N + 1)`
- old master behavior using `ewm(com=N)`
- fixed behavior using `ewm(span=N)`

The fixed version matches the reference exactly. The old version does not.

## Example 1: `momentum_feature/Po.py`

Formula in the file:

```text
EMA_SHORT = EMA(CLOSE, N)
EMA_LONG  = EMA(CLOSE, 3N)
PO = (EMA_SHORT - EMA_LONG) / EMA_LONG * 100
```

Tested on `AAPL`, `n = 14`.

### PO reference vs old vs fixed

| row | reference | old `com` | fixed `span` |
| --- | ---: | ---: | ---: |
| 20 | 2.4204 | 1.9865 | 2.4204 |
| 100 | 3.2294 | 5.3218 | 3.2294 |
| 500 | -0.4511 | 0.0906 | -0.4511 |
| 1000 | 1.0501 | -0.6581 | 1.0501 |
| 2000 | -2.2259 | -3.2037 | -2.2259 |

Result:

- `allclose(fix, reference) == True`
- `allclose(old, reference) == False`

## Example 2: `trend_feature/Tema.py`

Formula in the file:

```text
TEMA = 3*EMA(CLOSE,N) - 3*EMA(EMA(CLOSE,N),N) + EMA(EMA(EMA(CLOSE,N),N),N)
```

Tested on `AAPL`, `n = 20`.

### TEMA-derived result reference vs old vs fixed

| row | reference | old `com` | fixed `span` |
| --- | ---: | ---: | ---: |
| 100 | -0.023098 | -0.046930 | -0.023098 |
| 500 | 0.002085 | 0.010429 | 0.002085 |
| 1000 | -0.044531 | 0.009525 | -0.044531 |
| 2000 | 0.012962 | 0.040268 | 0.012962 |

Result:

- `allclose(fix, reference) == True`
- `allclose(old, reference) == False`

## Example 3: raw EMA on AAPL close, `n = 14`

Reference EMA uses `alpha = 2 / (14 + 1) = 0.133333`.

| row | close | reference `span=14` | old `com=14` | diff |
| --- | ---: | ---: | ---: | ---: |
| 20 | 22.56 | 22.2460 | 21.8933 | -0.3527 |
| 100 | 25.70 | 25.6921 | 25.2455 | -0.4466 |
| 1000 | 69.52 | 66.8970 | 66.0086 | -0.8884 |
| 2000 | 163.51 | 168.2220 | 170.2424 | 2.0203 |

Result:

- `allclose(span, reference) == True`
- `allclose(com, reference) == False`

## Scope of the fix

This fix applies only to files that used positional `ewm(...)` while the formula intended `EMA(..., N)`.

It does **not** apply to files that already use one of these explicit forms:

- `ewm(span=...)`
- `ewm(alpha=...)`
- `ewm(com=...)`
- `ewm(halflife=...)`

For example, `momentum_feature/Rsis.py` already uses `alpha=1 / (4 * n)`. That file was not part of this bug.

## Affected files

33 files in this branch use the corrected `span=` form in place of master's positional `ewm(...)`:

- `composite_feature/FearGreed_Yidai_v1.py`
- `momentum_feature/Bias_v11.py`
- `momentum_feature/CoppMinRoute.py`
- `momentum_feature/Do.py`
- `momentum_feature/Erbear.py`
- `momentum_feature/Erbull.py`
- `momentum_feature/MacdVol.py`
- `momentum_feature/MtmTb.py`
- `momentum_feature/MtmVolMean.py`
- `momentum_feature/PmoTema.py`
- `momentum_feature/Po.py`
- `momentum_feature/Ppo.py`
- `momentum_feature/Ppo_v1.py`
- `momentum_feature/Rsih.py`
- `momentum_feature/Smi.py`
- `momentum_feature/Sroc.py`
- `momentum_feature/SrocVol.py`
- `momentum_feature/Stc.py`
- `momentum_feature/Tsi.py`
- `momentum_feature/Zlmacd.py`
- `price_feature/Typ.py`
- `price_feature/Wc.py`
- `trend_feature/Dema.py`
- `trend_feature/Hullma.py`
- `trend_feature/T3.py`
- `trend_feature/Tema.py`
- `trend_feature/Trix.py`
- `volatility_feature/Apz.py`
- `volatility_feature/Cv.py`
- `volume_feature/Adosc.py`
- `volume_feature/Ko.py`
- `volume_feature/Pvo.py`
- `volume_feature/Tmf.py`

## Conclusion

The `ewm(n)` to `ewm(span=n)` change is a real bug fix.

The old code passed `n` as `com`, which does not match an `N` period EMA. The fixed code matches both:

1. pandas' documented API semantics
2. the indicator formulas written in the files
3. direct numerical reference calculations using `alpha = 2 / (N + 1)`
