import numpy as np


def signal(df, n, factor_name, config):
    # Cmo_v3 indicator (Smoothed CMO)
    # Formula: CMO = 100 * (SUM(up_diff,N) - SUM(|dn_diff|,N)) / (SUM(up_diff,N) + SUM(|dn_diff|,N))
    #          result = MA(CMO, N)
    # Standard Chande Momentum Oscillator smoothed by a rolling mean to reduce noise.
    # Range: [-100, 100] before smoothing. Positive = net upside momentum; negative = net downside.
    eps = config.eps
    df["momentum"] = df["close"] - df["close"].shift(1)
    df["up"] = np.where(df["momentum"] > 0, df["momentum"], 0)
    df["dn"] = np.where(df["momentum"] < 0, abs(df["momentum"]), 0)
    df["up_sum"] = df["up"].rolling(window=n, min_periods=config.min_periods).sum()
    df["dn_sum"] = df["dn"].rolling(window=n, min_periods=config.min_periods).sum()
    df["cmo"] = (df["up_sum"] - df["dn_sum"]) / (df["up_sum"] + df["dn_sum"] + eps) * 100
    df[factor_name] = df["cmo"].rolling(window=n, min_periods=config.min_periods).mean()

    # delete extra columns
    del df["momentum"], df["up"], df["dn"], df["up_sum"], df["dn_sum"], df["cmo"]

    return df
