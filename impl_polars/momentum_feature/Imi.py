import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # IMI indicator
    """
    N=14
    INC=SUM(IF(CLOSE>OPEN,CLOSE-OPEN,0),N)
    DEC=SUM(IF(OPEN>CLOSE,OPEN-CLOSE,0),N)
    IMI=INC/(INC+DEC)
    IMI is calculated similarly to RSI. The difference is that IMI uses
    close price and open price, while RSI uses close price and the previous day's close price.
    So RSI compares two consecutive days, while IMI compares within the same trading day.
    If IMI crosses above 80, a buy signal is generated; if IMI crosses below 20, a sell signal is generated.
    """
    df = df.with_columns(
        pl.Series("INC", np.where(df["close"] > df["open"], df["close"] - df["open"], 0)).fill_nan(None)
    )
    df = df.with_columns(pl.Series("INC_sum", df["INC"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(
        pl.Series("DEC", np.where(df["open"] > df["close"], df["open"] - df["close"], 0)).fill_nan(None)
    )
    df = df.with_columns(pl.Series("DEC_sum", df["DEC"].rolling_sum(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series(factor_name, df["INC_sum"] / (df["INC_sum"] + df["DEC_sum"])))

    df = df.drop("INC")
    df = df.drop("INC_sum")
    df = df.drop("DEC")
    df = df.drop("DEC_sum")

    return df
