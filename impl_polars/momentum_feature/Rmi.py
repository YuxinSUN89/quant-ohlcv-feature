import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # RMI indicator
    """
    N=7
    RMI=SMA(MAX(CLOSE-REF(CLOSE,4),0),N,1)/SMA(ABS(CLOSE-REF(CLOSE,1)),N,1)*100
    RMI is similar to RSI in calculation, but replaces the momentum term CLOSE-REF(CLOSE,1)
    with the difference from four days ago: CLOSE-REF(CLOSE,4).
    """
    df = df.with_columns(
        pl.Series(
            "max_close", np.where(df["close"] > df["close"].shift(4), df["close"] - df["close"].shift(4), 0)
        ).fill_nan(None)
    )
    df = df.with_columns(pl.Series("abs_close", df["close"] - df["close"].shift(1)))
    df = df.with_columns(pl.Series("sma_1", df["max_close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("sma_2", df["abs_close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series(factor_name, df["sma_1"] / df["sma_2"] * 100))

    df = df.drop("max_close")
    df = df.drop("abs_close")
    df = df.drop("sma_1")
    df = df.drop("sma_2")

    return df
