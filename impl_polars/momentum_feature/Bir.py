import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Bir indicator (Breakout Indicator using 4-price rolling max/min)
    # Formula: P = (OPEN+HIGH+LOW+CLOSE)/4; P_MAX = MAX(P,N); P_MIN = MIN(P,N)
    #          UP = MAX(P, REF(P_MAX, N/3)) - REF(P_MAX, N/3) normalized
    #          DOWN = MIN(P, REF(P_MIN, N/3)) - REF(P_MIN, N/3) normalized
    #          result = MA(UP + DOWN, N/3)
    # Measures breakouts above recent max and below recent min of the 4-price average.
    # Positive values indicate price broke above recent highs; negative indicates breakdown below lows.
    df = df.with_columns(pl.Series("p", (df["open"] + df["high"] + df["low"] + df["close"]) / 4.0))
    df = df.with_columns(pl.Series("p_max", df["p"].rolling_max(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("p_min", df["p"].rolling_min(n, min_samples=config.min_periods)))
    short_period = max(n // 3, 1)
    df = df.with_columns(
        pl.Series(
            "up", np.where(df["p"] > df["p_max"].shift(short_period), df["p"], df["p_max"].shift(short_period))
        ).fill_nan(None)
    )
    df = df.with_columns(
        pl.Series("up", (df["up"] - df["p_max"].shift(short_period)) / df["p_max"].shift(short_period))
    )
    df = df.with_columns(
        pl.Series(
            "down", np.where(df["p"] < df["p_min"].shift(short_period), df["p"], df["p_min"].shift(short_period))
        ).fill_nan(None)
    )
    df = df.with_columns(
        pl.Series("down", (df["down"] - df["p_min"].shift(short_period)) / df["p_min"].shift(short_period))
    )
    df = df.with_columns(
        pl.Series(factor_name, (df["up"] + df["down"]).rolling_mean(short_period, min_samples=config.min_periods))
    )

    df = df.drop(["p", "p_max", "p_min", "up", "down"])

    return df
