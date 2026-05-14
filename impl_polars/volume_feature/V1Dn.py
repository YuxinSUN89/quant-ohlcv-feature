import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # V1Dn indicator (V1 lower adaptive Bollinger band distance)
    # Formula: V1 composite = MTM_MEAN * WD_ATR * MTM_ATR * MTM_ATR_MEAN
    #          MEDIAN = MA(V1, N); STD = rolling std of V1
    #          Z_SCORE = |V1 - MEDIAN| / STD; M1 = ROLLING_MAX(Z_SCORE, N).shift(1)
    #          DN1 = MEDIAN - STD * M1; V1Dn = DN1 - V1
    # Measures how far the V1 composite falls below its adaptive lower Bollinger band.
    # Positive values indicate V1 is below the lower band (potential mean-reversion buy signal).
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
    indicator = pl.Series(indicator)

    # calculate adaptive Bollinger for the new strategy factor
    median = indicator.rolling_mean(n1, min_samples=config.min_periods)
    std = indicator.rolling_std(n1, ddof=config.ddof, min_samples=config.min_periods)
    z_score = abs(indicator - median) / std
    m1 = pl.Series(z_score).rolling_max(n1, min_samples=config.min_periods).shift(1)
    dn1 = median - std * m1
    indicator *= 1e8
    dn1 *= 1e8
    df = df.with_columns(pl.Series(factor_name, dn1 - indicator))

    return df
