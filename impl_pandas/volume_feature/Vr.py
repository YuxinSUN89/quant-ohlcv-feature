import numpy as np
import pandas as pd


def signal(df, n, factor_name, config):
    # Vr indicator (Volume Ratio)
    # Formula: AV = VOLUME if CLOSE > REF(CLOSE,1) else 0 (up-day volume)
    #          BV = VOLUME if CLOSE < REF(CLOSE,1) else 0 (down-day volume)
    #          CV = VOLUME if CLOSE == REF(CLOSE,1) else 0 (neutral volume)
    #          VR = (SUM(AV,N) + 0.5*SUM(CV,N)) / (SUM(BV,N) + 0.5*SUM(CV,N))
    # Measures the ratio of buying volume to selling volume over N periods. VR > 1 indicates
    # more buying than selling; VR < 1 indicates the opposite. Neutral volume is split equally.
    av = np.where(df["close"] > df["close"].shift(1), df["volume"], 0)
    bv = np.where(df["close"] < df["close"].shift(1), df["volume"], 0)
    _cv = np.where(df["close"] == df["close"].shift(1), df["volume"], 0)

    avs = pd.Series(av).rolling(n, min_periods=config.min_periods).sum()
    bvs = pd.Series(bv).rolling(n, min_periods=config.min_periods).sum()
    cvs = pd.Series(_cv).rolling(n, min_periods=config.min_periods).sum()

    s = (avs + 0.5 * cvs) / (config.normalize_eps + bvs + 0.5 * cvs)

    df[factor_name] = pd.Series(s)

    return df
