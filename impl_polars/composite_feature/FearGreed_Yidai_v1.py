import numpy as np
import polars as pl


# wma (weighted moving average)
def wma(df, column, k):
    weights = np.arange(1, k + 1)
    s = np.array(df[column], dtype=float)
    conv = np.convolve(s, weights[::-1] / weights.sum(), mode="valid")
    result = np.full(len(s), np.nan)
    result[k - 1 :] = conv
    return result.tolist()


# sma (simple moving average)
def sma(df, column, k, config):
    smas = df[column].rolling_mean(k, min_samples=config.min_periods)
    return smas


# ema (exponential smoothing moving average) - reserved
def ema(df, column, k, config):
    emas = df[column].ewm_mean(span=k, adjust=config.ewm_adjust)
    return emas


# Indicator name version: FearGreed_Yidai_v1
def signal(df, n, factor_name, config):
    # calculate TR (true amplitude), smooth and normalize (subsequent calculations use normalized parameters)
    df = df.with_columns(pl.Series("c1", df["high"] - df["low"]))  # HIGH-LOW
    df = df.with_columns(pl.Series("c2", (df["high"] - df["close"].shift(1)).abs()))  # ABS(HIGH-REF(CLOSE,1))
    df = df.with_columns(pl.Series("c3", (df["low"] - df["close"].shift(1)).abs()))  # ABS(LOW-REF(CLOSE,1))
    df = df.with_columns(TR=pl.max_horizontal([pl.col("c1"), pl.col("c2"), pl.col("c3")]))
    df = df.with_columns(pl.Series("sma", sma(df, column="close", k=n, config=config)))
    df = df.with_columns(pl.Series("STR", df["TR"] / (df["sma"] + config.eps)))

    # separate bull/bear amplitude
    df = df.with_columns(pl.Series("trUp", np.where(df["close"] > df["close"].shift(1), df["STR"], 0)).fill_nan(None))
    df = df.with_columns(pl.Series("trDn", np.where(df["close"] < df["close"].shift(1), df["STR"], 0)).fill_nan(None))

    # smooth bull/bear amplitude - fast and slow moving averages
    df = df.with_columns(pl.Series("wmatrUp1", wma(df, column="trUp", k=n)))
    df = df.with_columns(pl.Series("wmatrDn1", wma(df, column="trDn", k=n)))
    df = df.with_columns(pl.Series("wmatrUp2", wma(df, column="trUp", k=2 * n)))
    df = df.with_columns(pl.Series("wmatrDn2", wma(df, column="trDn", k=2 * n)))

    # compare bull/bear amplitude - first derivative describing speed, then smooth
    df = df.with_columns(pl.Series("fastDiff", df["wmatrUp1"] - df["wmatrDn1"]))
    df = df.with_columns(pl.Series("slowDiff", df["wmatrUp2"] - df["wmatrDn2"]))

    # compare fast and slow moving averages - second derivative describing acceleration
    df = df.with_columns(pl.Series("FastMinusSlow", df["fastDiff"] - df["slowDiff"]))
    df = df.with_columns(pl.Series("fgi", wma(df, column="FastMinusSlow", k=n)))

    # return df
    df = df.with_columns(pl.Series(factor_name, df["fgi"]))

    # delete extra columns
    df = df.drop(["c1", "c2", "c3", "TR", "STR", "sma"])
    df = df.drop(["trUp", "trDn", "fastDiff", "slowDiff", "FastMinusSlow", "fgi"])
    df = df.drop(["wmatrUp1", "wmatrDn1", "wmatrUp2", "wmatrDn2"])

    return df
