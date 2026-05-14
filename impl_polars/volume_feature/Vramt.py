import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    """
    N=40
    AV=IF(CLOSE>REF(CLOSE,1),AMOUNT,0)
    BV=IF(CLOSE<REF(CLOSE,1),AMOUNT,0)
    CV=IF(CLOSE=REF(CLOSE,1),AMOUNT,0)
    AVS=SUM(AV,N)
    BVS=SUM(BV,N)
    CVS=SUM(CV,N)
    VRAMT=(AVS+CVS/2)/(BVS+CVS/2)
    VRAMT is calculated the same as the VR indicator (Volume Ratio), but replaces
    trading volume with trading amount.
    A buy signal is generated when VRAMT crosses above 180;
    a sell signal is generated when VRAMT crosses below 70.
    """
    eps = config.eps
    df = df.with_columns(pl.Series("AV", np.where(df["close"] > df["close"].shift(1), df["volume"], 0)).fill_nan(None))
    df = df.with_columns(pl.Series("BV", np.where(df["close"] < df["close"].shift(1), df["volume"], 0)).fill_nan(None))
    df = df.with_columns(pl.Series("CV", np.where(df["close"] == df["close"].shift(1), df["volume"], 0)).fill_nan(None))
    df = df.with_columns(pl.Series("AVS", df["AV"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("BVS", df["BV"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("CVS", df["CV"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series(factor_name, (df["AVS"] + df["CVS"] / 2) / (df["BVS"] + df["CVS"] / 2 + eps)))

    df = df.drop(["AV", "BV", "CV", "AVS", "BVS", "CVS"])

    return df
