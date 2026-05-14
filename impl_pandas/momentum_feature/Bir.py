import numpy as np


def signal(df, n, factor_name, config):
    # Bir indicator (Breakout Indicator using 4-price rolling max/min)
    # Formula: P = (OPEN+HIGH+LOW+CLOSE)/4; P_MAX = MAX(P,N); P_MIN = MIN(P,N)
    #          UP = MAX(P, REF(P_MAX, N/3)) - REF(P_MAX, N/3) normalized
    #          DOWN = MIN(P, REF(P_MIN, N/3)) - REF(P_MIN, N/3) normalized
    #          result = MA(UP + DOWN, N/3)
    # Measures breakouts above recent max and below recent min of the 4-price average.
    # Positive values indicate price broke above recent highs; negative indicates breakdown below lows.
    df["p"] = (df["open"] + df["high"] + df["low"] + df["close"]) / 4.0
    df["p_max"] = df["p"].rolling(n, min_periods=config.min_periods).max()
    df["p_min"] = df["p"].rolling(n, min_periods=config.min_periods).min()
    short_period = max(n // 3, 1)
    df["up"] = np.where(df["p"] > df["p_max"].shift(short_period), df["p"], df["p_max"].shift(short_period))
    df["up"] = (df["up"] - df["p_max"].shift(short_period)) / df["p_max"].shift(short_period)
    df["down"] = np.where(df["p"] < df["p_min"].shift(short_period), df["p"], df["p_min"].shift(short_period))
    df["down"] = (df["down"] - df["p_min"].shift(short_period)) / df["p_min"].shift(short_period)
    df[factor_name] = (df["up"] + df["down"]).rolling(short_period, min_periods=config.min_periods).mean()

    del df["p"], df["p_max"], df["p_min"], df["up"], df["down"]

    return df
