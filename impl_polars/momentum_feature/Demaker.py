import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Demaker indicator
    """
    N=20
    Demax=HIGH-REF(HIGH,1)
    Demax=IF(Demax>0,Demax,0)
    Demin=REF(LOW,1)-LOW
    Demin=IF(Demin>0,Demin,0)
    Demaker=MA(Demax,N)/(MA(Demax,N)+MA(Demin,N))
    When Demaker>0.7, the uptrend is strong; when Demaker<0.3, the downtrend is strong.
    When Demaker crosses above 0.7 / crosses below 0.3, a buy/sell signal is generated.
    """
    df = df.with_columns(pl.Series("Demax", df["high"] - df["high"].shift(1)))
    df = df.with_columns(pl.Series("Demax", np.where(df["Demax"] > 0, df["Demax"], 0)).fill_nan(None))
    df = df.with_columns(pl.Series("Demin", df["low"].shift(1) - df["low"]))
    df = df.with_columns(pl.Series("Demin", np.where(df["Demin"] > 0, df["Demin"], 0)).fill_nan(None))
    df = df.with_columns(pl.Series("Demax_ma", df["Demax"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("Demin_ma", df["Demin"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series(factor_name, df["Demax_ma"] / (df["Demax_ma"] + df["Demin_ma"])))

    df = df.drop("Demax")
    df = df.drop("Demin")
    df = df.drop("Demax_ma")
    df = df.drop("Demin_ma")

    return df
