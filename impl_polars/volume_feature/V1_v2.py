import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # V1_v2 indicator (same composite as V1)
    # Formula: MTM_MEAN = MA(CLOSE/REF(CLOSE,N)-1, N); WD_ATR = ATR(N) / MA(CLOSE,N)
    #          MTM_ATR = ATR of momentum returns; MTM_ATR_MEAN = ATR of rolling-mean momentum returns
    #          V1 = MTM_MEAN * WD_ATR * MTM_ATR * MTM_ATR_MEAN
    # A composite momentum-volatility factor. Momentum mean is amplified by three ATR-based
    # volatility measures: price ATR ratio, momentum ATR, and smoothed momentum ATR.
    n1 = n
    # calculate momentum factor
    mtm = df["close"] / (df["close"].shift(n1) + config.eps) - 1
    mtm_mean = mtm.rolling_mean(n1, min_samples=config.min_periods)

    # calculate volatility factor wd_atr based on price atr
    c1 = df["high"] - df["low"]
    c2 = abs(df["high"] - df["close"].shift(1))
    c3 = abs(df["low"] - df["close"].shift(1))
    tr = np.max(np.array([c1, c2, c3]), axis=0)  # take the maximum of the three series
    atr = pl.Series(tr).rolling_mean(n1, min_samples=config.min_periods)
    avg_price = df["close"].rolling_mean(n1, min_samples=config.min_periods)
    wd_atr = atr / avg_price  # === volatility factor

    # calculate volatility factor for MTM indicator referencing ATR
    mtm_l = df["low"] / df["low"].shift(n1) - 1
    mtm_h = df["high"] / df["high"].shift(n1) - 1
    mtm_c = df["close"] / (df["close"].shift(n1) + config.eps) - 1
    mtm_c1 = mtm_h - mtm_l
    mtm_c2 = abs(mtm_h - mtm_c.shift(1))
    mtm_c3 = abs(mtm_l - mtm_c.shift(1))
    mtm_tr = np.max(np.array([mtm_c1, mtm_c2, mtm_c3]), axis=0)  # take the maximum of the three series
    mtm_atr = pl.Series(mtm_tr).rolling_mean(n1, min_samples=config.min_periods)  # === mtm volatility factor

    # calculate volatility factor for MTM mean indicator referencing ATR
    mtm_l_mean = mtm_l.rolling_mean(n1, min_samples=config.min_periods)
    mtm_h_mean = mtm_h.rolling_mean(n1, min_samples=config.min_periods)
    mtm_c_mean = mtm_c.rolling_mean(n1, min_samples=config.min_periods)
    mtm_c1 = mtm_h_mean - mtm_l_mean
    mtm_c2 = abs(mtm_h_mean - mtm_c_mean.shift(1))
    mtm_c3 = abs(mtm_l_mean - mtm_c_mean.shift(1))
    mtm_tr = np.max(np.array([mtm_c1, mtm_c2, mtm_c3]), axis=0)  # take the maximum of the three series
    mtm_atr_mean = pl.Series(mtm_tr).rolling_mean(n1, min_samples=config.min_periods)  # === mtm_mean volatility factor

    indicator = mtm_mean
    # multiply mtm_mean indicator by the three volatility factors respectively
    indicator *= wd_atr * mtm_atr * mtm_atr_mean
    df = df.with_columns(pl.Series(factor_name, indicator))

    return df
