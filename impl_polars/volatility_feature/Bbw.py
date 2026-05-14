import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Bbw indicator (BBW change × momentum × RSI composite)
    # Formula: RSI = 100 * A/(A+B) where A=SUM(up_diff,N), B=SUM(down_diff,N)
    #          BBW = STD(CLOSE,N)/MA(CLOSE,N); BBW_CHG = BBW.diff(N)
    #          result = BBW_CHG * (CLOSE/REF(CLOSE,N) - 1) * RSI
    # Combines Bollinger bandwidth change (volatility expansion/contraction) with N-period
    # momentum and RSI. Positive values indicate expanding volatility with upside momentum.
    eps = config.eps
    close_dif = df["close"].diff()
    df = df.with_columns(pl.Series("up", np.where(close_dif > 0, close_dif, 0)).fill_nan(None))
    df = df.with_columns(pl.Series("down", np.where(close_dif < 0, abs(close_dif), 0)).fill_nan(None))
    a = df["up"].rolling_sum(n, min_samples=config.min_periods)
    b = df["down"].rolling_sum(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series("rsi", (a / (a + b)) * 100))
    df = df.with_columns(pl.Series("median", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("std", df["close"].rolling_std(n, ddof=config.ddof, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("bbw", (df["std"] / (df["median"] + config.eps)).diff(n)))
    df = df.with_columns(
        pl.Series(factor_name, (df["bbw"]) * (df["close"] / (df["close"].shift(n) + config.eps) - 1 + eps) * df["rsi"])
    )

    df = df.drop(["up", "down", "rsi", "median"])
    df = df.drop(["std", "bbw"])

    return df
