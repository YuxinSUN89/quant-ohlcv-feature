import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # RSIV indicator
    """
    N=20
    VOLUP=IF(CLOSE>REF(CLOSE,1),VOLUME,0)
    VOLDOWN=IF(CLOSE<REF(CLOSE,1),VOLUME,0)
    SUMUP=SUM(VOLUP,N)
    SUMDOWN=SUM(VOLDOWN,N)
    RSIV=100*SUMUP/(SUMUP+SUMDOWN)
    RSIV is calculated like RSI, but the price change CLOSE-REF(CLOSE,1) is replaced
    with volume VOLUME. Usage is similar to RSI. Here we use it as a momentum indicator;
    buy when it crosses above 60, sell when it crosses below 40.
    """
    df = df.with_columns(
        pl.Series("VOLUP", np.where(df["close"] > df["close"].shift(1), df["volume"], 0)).fill_nan(None)
    )
    df = df.with_columns(
        pl.Series("VOLDOWN", np.where(df["close"] < df["close"].shift(1), df["volume"], 0)).fill_nan(None)
    )
    df = df.with_columns(pl.Series("SUMUP", df["VOLUP"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("SUMDOWN", df["VOLDOWN"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series(factor_name, df["SUMUP"] / (df["SUMUP"] + df["SUMDOWN"]) * 100))

    df = df.drop("VOLUP")
    df = df.drop("VOLDOWN")
    df = df.drop("SUMUP")
    df = df.drop("SUMDOWN")

    return df
