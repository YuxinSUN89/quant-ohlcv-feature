import numpy as np


# wma (weighted moving average)
def wma(df, column, k, config):
    weights = np.arange(1, k + 1)
    wmas = df[column].rolling(k, min_periods=k).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True).to_list()
    return wmas


# sma (simple moving average)
def sma(df, column, k, config):
    smas = df[column].rolling(k, min_periods=config.min_periods).mean()
    return smas


# ema (exponential smoothing moving average) - reserved
def ema(df, column, k, config):
    emas = df[column].ewm(span=k, adjust=config.ewm_adjust).mean()
    return emas


# Indicator name version: FearGreed_Yidai_v1
def signal(df, n, factor_name, config):
    # calculate TR (true amplitude), smooth and normalize (subsequent calculations use normalized parameters)
    df["c1"] = df["high"] - df["low"]  # HIGH-LOW
    df["c2"] = abs(df["high"] - df["close"].shift(1))  # ABS(HIGH-REF(CLOSE,1)
    df["c3"] = abs(df["low"] - df["close"].shift(1))  # ABS(LOW-REF(CLOSE,1))
    df["TR"] = df[["c1", "c2", "c3"]].max(axis=1)
    df["sma"] = sma(df, column="close", k=n, config=config)
    df["STR"] = df["TR"] / (df["sma"] + config.eps)

    # separate bull/bear amplitude
    df["trUp"] = np.where(df["close"] > df["close"].shift(1), df["STR"], 0)
    df["trDn"] = np.where(df["close"] < df["close"].shift(1), df["STR"], 0)

    # smooth bull/bear amplitude - fast and slow moving averages
    df["wmatrUp1"] = wma(df, column="trUp", k=n, config=config)
    df["wmatrDn1"] = wma(df, column="trDn", k=n, config=config)
    df["wmatrUp2"] = wma(df, column="trUp", k=2 * n, config=config)
    df["wmatrDn2"] = wma(df, column="trDn", k=2 * n, config=config)

    # compare bull/bear amplitude - first derivative describing speed, then smooth
    df["fastDiff"] = df["wmatrUp1"] - df["wmatrDn1"]
    df["slowDiff"] = df["wmatrUp2"] - df["wmatrDn2"]

    # compare fast and slow moving averages - second derivative describing acceleration
    df["FastMinusSlow"] = df["fastDiff"] - df["slowDiff"]
    df["fgi"] = wma(df, column="FastMinusSlow", k=n, config=config)

    # return df
    df[factor_name] = df["fgi"]

    # delete extra columns
    del df["c1"], df["c2"], df["c3"], df["TR"], df["STR"], df["sma"]
    del df["trUp"], df["trDn"], df["fastDiff"], df["slowDiff"], df["FastMinusSlow"], df["fgi"]
    del df["wmatrUp1"], df["wmatrDn1"], df["wmatrUp2"], df["wmatrDn2"]

    return df
