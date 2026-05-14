import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Cmo_v3 indicator (Smoothed CMO)
    # Formula: CMO = 100 * (SUM(up_diff,N) - SUM(|dn_diff|,N)) / (SUM(up_diff,N) + SUM(|dn_diff|,N))
    #          result = MA(CMO, N)
    # Standard Chande Momentum Oscillator smoothed by a rolling mean to reduce noise.
    # Range: [-100, 100] before smoothing. Positive = net upside momentum; negative = net downside.
    eps = config.eps
    df = df.with_columns(pl.Series("momentum", df["close"] - df["close"].shift(1)))
    df = df.with_columns(pl.Series("up", np.where(df["momentum"] > 0, df["momentum"], 0)).fill_nan(None))
    df = df.with_columns(pl.Series("dn", np.where(df["momentum"] < 0, abs(df["momentum"]), 0)).fill_nan(None))
    df = df.with_columns(pl.Series("up_sum", df["up"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("dn_sum", df["dn"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("cmo", (df["up_sum"] - df["dn_sum"]) / (df["up_sum"] + df["dn_sum"] + eps) * 100))
    df = df.with_columns(pl.Series(factor_name, df["cmo"].rolling_mean(n, min_samples=config.min_periods)))

    # delete extra columns
    df = df.drop(["momentum", "up", "dn", "up_sum", "dn_sum", "cmo"])

    return df
