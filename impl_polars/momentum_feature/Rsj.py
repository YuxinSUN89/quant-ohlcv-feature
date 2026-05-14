import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Rsj indicator (RSJ — ratio of up/down realized variance)
    # Formula: RV = SUM(return^2, N); RV+ = SUM(max(return,0)^2, N); RV- = SUM(min(return,0)^2, N)
    #          RSJ = (RV+ - RV-) / RV
    # Measures the asymmetry between upside and downside realized variance.
    # Positive values indicate right-skewed returns (more upside variance); negative indicate left-skewed.
    eps = config.eps
    # calculate returns
    df = df.with_columns(pl.Series("return", df["close"] / (df["close"].shift(1) + config.eps) - 1))

    # calculate RV
    df = df.with_columns(pl.Series("pow_return", pow(df["return"], 2)))
    df = df.with_columns(pl.Series("rv", df["pow_return"].rolling_sum(n, min_samples=config.min_periods)))

    # calculate RV +/-
    df = df.with_columns(pl.Series("positive_data", np.where(df["return"] > 0, df["return"], 0)).fill_nan(None))
    df = df.with_columns(pl.Series("negative_data", np.where(df["return"] < 0, df["return"], 0)).fill_nan(None))
    df = df.with_columns(pl.Series("pow_positive_data", pow(df["positive_data"], 2)))
    df = df.with_columns(pl.Series("pow_negetive_data", pow(df["negative_data"], 2)))
    df = df.with_columns(pl.Series("rv+", df["pow_positive_data"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("rv-", df["pow_negetive_data"].rolling_sum(n, min_samples=config.min_periods)))

    # calculate RSJ
    df = df.with_columns(pl.Series(factor_name, (df["rv+"] - df["rv-"]) / (df["rv"] + eps)))

    # remove redundant columns
    df = df.drop(["return", "rv", "positive_data", "negative_data"])
    df = df.drop(["rv+", "rv-", "pow_positive_data", "pow_negetive_data"])

    return df
