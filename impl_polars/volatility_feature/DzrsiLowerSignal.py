import numpy as np
import polars as pl


# ===== function: zscore normalization
def scale_zscore(_s, _n, config):
    s = pl.Series(_s)
    zscore = (s - s.rolling_mean(_n, min_samples=config.min_periods)) / s.rolling_std(
        _n, min_samples=config.min_periods, ddof=config.ddof
    )
    # replace ±inf (std=0 edge cases) with NaN; keep float NaN as float NaN so that
    # polars mean()/std() propagate NaN (treated as missing by compare.py, same as pandas)
    arr = np.array(zscore.to_list(), dtype=float)
    arr[np.isinf(arr)] = np.nan
    return pl.Series(arr)


def signal(df, n, factor_name, config):
    # DzrsiLowerSignal indicator (RSI Bollinger Lower band - RSI half-period MA, z-score normalized)
    # Formula: RSI = A / (A + B) where A=SUM(up_diff,N), B=SUM(down_diff,N)
    #          RSI_LOWER = MA(RSI,N) - 2*STD(RSI,N); RSI_MA = MA(RSI, N/2)
    #          result = ZSCORE(RSI_LOWER - RSI_MA, N)
    # Applies Bollinger Band logic to RSI. Measures how far the RSI lower band is below the
    # RSI half-period MA, z-score normalized. Negative values suggest RSI is below its lower band (oversold).
    rtn = df["close"].diff()
    up = np.where(rtn > 0, rtn, 0)
    up = pl.Series(up).fill_nan(None)
    dn = np.where(rtn < 0, rtn.abs(), 0)
    dn = pl.Series(dn).fill_nan(None)
    a = pl.Series(up).rolling_sum(n, min_samples=config.min_periods)
    b = pl.Series(dn).rolling_sum(n, min_samples=config.min_periods)

    a *= 1e3
    b *= 1e3

    rsi = a / (config.normalize_eps + a + b)

    rsi_middle = rsi.rolling_mean(n, min_samples=config.min_periods)
    rsi_lower = rsi_middle - 2 * rsi.rolling_std(n, min_samples=config.min_periods, ddof=config.ddof)
    rsi_ma = rsi.rolling_mean(int(n / 2), min_samples=config.min_periods)

    s = rsi_lower - rsi_ma
    df = df.with_columns(pl.Series(factor_name, scale_zscore(s, n, config=config)))

    return df
