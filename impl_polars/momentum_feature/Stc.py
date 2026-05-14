import numpy as np
import polars as pl


def _rolling_mean_np(arr, n, min_periods):
    a = np.asarray(arr, dtype=float)
    out = np.full(len(a), np.nan)
    min_p = min_periods or 1
    for i in range(len(a)):
        start = max(0, i - n + 1)
        w = a[start : i + 1]
        valid = w[~np.isnan(w)]
        if len(valid) < min_p:
            continue
        out[i] = valid.mean()
    return out


def _rolling_min_np(arr, n, min_periods):
    a = np.asarray(arr, dtype=float)
    out = np.full(len(a), np.nan)
    min_p = min_periods or 1
    for i in range(len(a)):
        start = max(0, i - n + 1)
        w = a[start : i + 1]
        valid = w[~np.isnan(w)]
        if len(valid) < min_p:
            continue
        out[i] = valid.min()
    return out


def _rolling_max_np(arr, n, min_periods):
    a = np.asarray(arr, dtype=float)
    out = np.full(len(a), np.nan)
    min_p = min_periods or 1
    for i in range(len(a)):
        start = max(0, i - n + 1)
        w = a[start : i + 1]
        valid = w[~np.isnan(w)]
        if len(valid) < min_p:
            continue
        out[i] = valid.max()
    return out


def signal(df, n, factor_name, config):
    # STC indicator
    """
    N1=23
    N2=50
    N=40
    MACDX=EMA(CLOSE,N1)-EMA(CLOSE,N2)
    V1=MIN(MACDX,N)
    V2=MAX(MACDX,N)-V1
    FK=IF(V2>0,(MACDX-V1)/V2*100,REF(FK,1))
    FD=SMA(FK,N,1)
    V3=MIN(FD,N)
    V4=MAX(FD,N)-V3
    SK=IF(V4>0,(FD-V3)/V4*100,REF(SK,1))
    STC=SD=SMA(SK,N,1)
    STC combines the algorithms of MACD and KDJ. First it computes MACD from the difference
    between short and long moving averages, then computes fast stochastic FK and FD of MACD,
    and finally computes the slow stochastic SK and SD of MACD. The slow stochastic is the STC.
    STC can reflect overbought/oversold conditions. Generally, STC > 75 is overbought, STC < 25 is oversold.
    A buy signal is generated when STC crosses above 25;
    a sell signal is generated when STC crosses below 75.
    """
    N1 = n
    N2 = int(N1 * 1.5)  # approximate value
    N = 2 * n
    # Numerical sensitivity note:
    # STC stacks EMA, rolling min/max, and recursive fallback (REF(previous FK/SK)).
    # Tiny floating-point differences can therefore accumulate into small output drift,
    # even when the overall shape is matched between pandas and polars.
    ema1 = df["close"].ewm_mean(span=N1, adjust=config.ewm_adjust).to_numpy()
    ema2 = df["close"].ewm_mean(span=N, adjust=config.ewm_adjust).to_numpy()
    macdx = ema1 - ema2
    v1 = _rolling_min_np(macdx, N2, config.min_periods)
    v2 = _rolling_max_np(macdx, N2, config.min_periods) - v1
    fk_base = (macdx - v1) / v2 * 100
    fk_prev = np.roll(fk_base, 1)
    fk_prev[0] = np.nan
    fk = np.where(v2 > 0, fk_base, fk_prev)
    fd = _rolling_mean_np(fk, N2, config.min_periods)
    v3 = _rolling_min_np(fd, N2, config.min_periods)
    v4 = _rolling_max_np(fd, N2, config.min_periods) - v3
    sk_base = (fd - v3) / v4 * 100
    sk_prev = np.roll(sk_base, 1)
    sk_prev[0] = np.nan
    sk = np.where(v4 > 0, sk_base, sk_prev)
    stc = _rolling_mean_np(sk, N1, config.min_periods)
    df = df.with_columns(pl.Series(factor_name, stc))
    return df
