import numpy as np


def signal(df, n, factor_name, config):
    # Rsj indicator (RSJ — ratio of up/down realized variance)
    # Formula: RV = SUM(return^2, N); RV+ = SUM(max(return,0)^2, N); RV- = SUM(min(return,0)^2, N)
    #          RSJ = (RV+ - RV-) / RV
    # Measures the asymmetry between upside and downside realized variance.
    # Positive values indicate right-skewed returns (more upside variance); negative indicate left-skewed.
    eps = config.eps
    # calculate returns
    df["return"] = df["close"] / df["close"].shift(1) - 1

    # calculate RV
    df["pow_return"] = pow(df["return"], 2)
    df["rv"] = df["pow_return"].rolling(window=n, min_periods=config.min_periods).sum()

    # calculate RV +/-
    df["positive_data"] = np.where(df["return"] > 0, df["return"], 0)
    df["negative_data"] = np.where(df["return"] < 0, df["return"], 0)
    df["pow_positive_data"] = pow(df["positive_data"], 2)
    df["pow_negetive_data"] = pow(df["negative_data"], 2)
    df["rv+"] = df["pow_positive_data"].rolling(window=n, min_periods=config.min_periods).sum()
    df["rv-"] = df["pow_negetive_data"].rolling(window=n, min_periods=config.min_periods).sum()

    # calculate RSJ
    df[factor_name] = (df["rv+"] - df["rv-"]) / (df["rv"] + eps)

    # remove redundant columns
    del df["return"], df["rv"], df["positive_data"], df["negative_data"]
    del df["rv+"], df["rv-"], df["pow_positive_data"], df["pow_negetive_data"]

    return df
