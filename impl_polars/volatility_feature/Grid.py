import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Grid indicator (z-score grid position percentage change)
    # Formula: MA = MA(CLOSE,N); STD = STD(CLOSE,N)
    #          GRID = MA((CLOSE - MA) / STD, N)  (rolling mean of z-scores)
    #          result = GRID.pct_change(N)
    # Measures the N-period rate of change of the smoothed z-score position.
    # Captures acceleration of price relative to its own volatility band.
    df = df.with_columns(pl.Series("median", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("std", df["close"].rolling_std(n, min_samples=config.min_periods, ddof=config.ddof)))
    df = df.with_columns(pl.Series("grid", (df["close"] - df["median"]) / (df["std"] + config.eps)))
    df = df.with_columns(pl.Series("grid", df["grid"].replace([np.inf, -np.inf], np.nan)))
    # fill_nan(None): convert float NaN to polars null so rolling_mean skips them (matching pandas)
    # DO NOT fill_null(0): early zero rows cause div-by-zero in pct_change → inf
    df = df.with_columns(pl.col("grid").fill_nan(None).alias("grid"))
    df = df.with_columns(pl.Series("grid", df["grid"].rolling_mean(n, min_samples=config.min_periods)))
    # pct_change with denominator floor: avoids FP amplification when rolling-mean-of-zscores ≈ 0
    grid_arr = np.array(df["grid"].to_list(), dtype=float)
    prev = np.concatenate([[np.nan] * n, grid_arr[:-n]])
    result = (grid_arr - prev) / np.where(np.abs(prev) > config.normalize_eps, prev, np.nan)
    df = df.with_columns(pl.Series(factor_name, result).fill_nan(None))
    # df['gridInt'] = df['grid'].astype("int")
    # df[factor_name] = df['gridInt'].pct_change(n)

    df = df.drop(["median", "std", "grid"])

    return df
