import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Vr indicator (Volume Ratio)
    # Formula: AV = VOLUME if CLOSE > REF(CLOSE,1) else 0 (up-day volume)
    #          BV = VOLUME if CLOSE < REF(CLOSE,1) else 0 (down-day volume)
    #          CV = VOLUME if CLOSE == REF(CLOSE,1) else 0 (neutral volume)
    #          VR = (SUM(AV,N) + 0.5*SUM(CV,N)) / (SUM(BV,N) + 0.5*SUM(CV,N))
    # Measures the ratio of buying volume to selling volume over N periods. VR > 1 indicates
    # more buying than selling; VR < 1 indicates the opposite. Neutral volume is split equally.
    av = np.where(df["close"] > df["close"].shift(1), df["volume"], 0)
    av = pl.Series(av).fill_nan(None)
    bv = np.where(df["close"] < df["close"].shift(1), df["volume"], 0)
    bv = pl.Series(bv).fill_nan(None)
    _cv = np.where(df["close"] == df["close"].shift(1), df["volume"], 0)
    _cv = pl.Series(_cv).fill_nan(None)

    avs = pl.Series(av).rolling_sum(n, min_samples=config.min_periods)
    bvs = pl.Series(bv).rolling_sum(n, min_samples=config.min_periods)
    cvs = pl.Series(_cv).rolling_sum(n, min_samples=config.min_periods)

    s = (avs + 0.5 * cvs) / (config.normalize_eps + bvs + 0.5 * cvs)

    df = df.with_columns(pl.Series(factor_name, s))

    return df
