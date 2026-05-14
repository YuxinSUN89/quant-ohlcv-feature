import numpy as np
import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # Adtm indicator
    """
    N=20
    DTM=IF(OPEN>REF(OPEN,1),MAX(HIGH-OPEN,OPEN-REF(OP
    EN,1)),0)
    DBM=IF(OPEN<REF(OPEN,1),MAX(OPEN-LOW,REF(OPEN,1)-O
    PEN),0)
    STM=SUM(DTM,N)
    SBM=SUM(DBM,N)
    Adtm=(STM-SBM)/MAX(STM,SBM)
    Adtm measures market sentiment by comparing how much the open price rises vs. falls.
    Adtm values range from -1 to 1. When Adtm crosses above 0.5, market sentiment is strong;
    when Adtm crosses below -0.5, market sentiment is weak. We generate trading signals accordingly.
    A buy signal is generated when Adtm crosses above 0.5;
    a sell signal is generated when Adtm crosses below -0.5.

    """
    tmp1_s = df["high"] - df["open"]  # HIGH-OPEN
    tmp2_s = df["open"] - df["open"].shift(1)  # OPEN-REF(OPEN,1)
    tmp3_s = df["open"] - df["low"]  # OPEN-LOW
    tmp4_s = df["open"].shift(1) - df["open"]  # REF(OPEN,1)-OPEN

    dtm = np.where(df["open"] > df["open"].shift(1), np.maximum(tmp1_s, tmp2_s), 0)
    dtm = pl.Series(dtm).fill_nan(None)
    dbm = np.where(df["open"] < df["open"].shift(1), np.maximum(tmp3_s, tmp4_s), 0)
    dbm = pl.Series(dbm).fill_nan(None)
    stm = pl.Series(dtm).rolling_sum(n, min_samples=config.min_periods)
    sbm = pl.Series(dbm).rolling_sum(n, min_samples=config.min_periods)

    signal = (stm - sbm) / (config.normalize_eps + np.maximum(stm, sbm))
    signal = df["close"] - signal
    df = df.with_columns(pl.Series(factor_name, scale_01(signal, n, config.normalize_eps, config=config)))

    return df
