import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Cmo_v2 indicator (CMO variant using rolling max instead of sum)
    # Formula: CMO_v2 = (MAX(up_diff, N) - MAX(|dn_diff|, N)) / (MAX(up_diff, N) + MAX(|dn_diff|, N))
    # A variant of the Chande Momentum Oscillator that uses the rolling maximum of up/down moves
    # instead of their sum, making it more sensitive to extreme price swings.
    # Range: [-1, 1]. Positive = upside momentum; negative = downside momentum.
    eps = config.eps
    df = df.with_columns(pl.Series("momentum", df["close"] - df["close"].shift(1)))
    df = df.with_columns(pl.Series("up", np.where(df["momentum"] > 0, df["momentum"], 0)).fill_nan(None))
    df = df.with_columns(pl.Series("dn", np.where(df["momentum"] < 0, abs(df["momentum"]), 0)).fill_nan(None))
    df = df.with_columns(pl.Series("up_sum", df["up"].rolling_max(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("dn_sum", df["dn"].rolling_max(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series(factor_name, (df["up_sum"] - df["dn_sum"]) / (df["up_sum"] + df["dn_sum"] + eps)))

    # delete extra columns
    df = df.drop(["momentum", "up", "dn", "up_sum", "dn_sum"])

    return df
