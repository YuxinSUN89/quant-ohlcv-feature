import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # RVI indicator
    """
    N1=10
    N2=20
    STD=STD(CLOSE,N)
    USTD=SUM(IF(CLOSE>REF(CLOSE,1),STD,0),N2)
    DSTD=SUM(IF(CLOSE<REF(CLOSE,1),STD,0),N2)
    RVI=100*USTD/(USTD+DSTD)
    RVI is calculated the same way as RSI, but replaces the closing price change in RSI
    with the standard deviation of the closing price over a past period, reflecting the
    comparison between upward and downward volatility. We can also compute USTD_MA and
    DSTD_MA (moving averages of USTD and DSTD) and then derive RVI=100*USTD_MA/(USTD_MA+DSTD_MA),
    just as with RSI. RVI is used the same way as RSI. When RVI > 70, the market is in a
    strong uptrend or overbought; when RVI < 30, the market is in a strong downtrend or oversold.
    When RVI drops below 30 then crosses back above 30, prices are expected to rebound from oversold;
    when RVI exceeds 70 then crosses below 70, the market is expected to pull back from overbought.
    A buy signal is generated when RVI crosses above 30;
    a sell signal is generated when RVI crosses below 70.
    """
    df = df.with_columns(pl.Series("std", df["close"].rolling_std(n, ddof=config.ddof, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("ustd", np.where(df["close"] > df["close"].shift(1), df["std"], 0)).fill_nan(None))
    df = df.with_columns(pl.Series("sum_ustd", df["ustd"].rolling_sum(2 * n, min_samples=config.min_periods)))

    df = df.with_columns(pl.Series("dstd", np.where(df["close"] < df["close"].shift(1), df["std"], 0)).fill_nan(None))
    df = df.with_columns(pl.Series("sum_dstd", df["dstd"].rolling_sum(2 * n, min_samples=config.min_periods)))

    df = df.with_columns(
        pl.Series(factor_name, (df["sum_ustd"] / (df["sum_ustd"] + df["sum_dstd"])).fill_nan(None) * 100)
    )

    df = df.drop("std")
    df = df.drop("ustd")
    df = df.drop("sum_ustd")
    df = df.drop("dstd")
    df = df.drop("sum_dstd")

    return df
