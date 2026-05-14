import polars as pl

from impl_polars.helpers import sma_recursive


def signal(df, n, factor_name, config):
    # RCCD indicator
    """
    M=40
    N1=20
    N2=40
    RC=CLOSE/REF(CLOSE,M)
    ARC1=SMA(REF(RC,1),M,1)
    DIF=MA(REF(ARC1,1),N1)-MA(REF(ARC1,1),N2)
    RCCD=SMA(DIF,M,1)
    RC is the ratio of the current price to the previous day's price. When RC > 1, prices are rising;
    when RC increases, the rate of price increase is accelerating. When RC < 1, prices are falling;
    when RC decreases, the rate of decline is accelerating. RCCD first smooths the RC indicator,
    then takes the difference between moving averages of different time lengths, then takes another
    moving average. Buy/sell signals are generated when RCCD crosses above/below 0.
    """
    df = df.with_columns(pl.Series("RC", df["close"] / (df["close"].shift(2 * n) + config.eps)))
    df = df.with_columns(pl.Series("ARC1", sma_recursive(df["RC"], n, 1)))
    df = df.with_columns(pl.Series("MA1", df["ARC1"].shift(1).rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("MA2", df["ARC1"].shift(1).rolling_mean(2 * n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("DIF", df["MA1"] - df["MA2"]))
    df = df.with_columns(pl.Series(factor_name, sma_recursive(df["DIF"], n, 1)))

    df = df.drop("RC")
    df = df.drop("ARC1")
    df = df.drop("MA1")
    df = df.drop("MA2")
    df = df.drop("DIF")

    return df
