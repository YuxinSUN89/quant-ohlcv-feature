import polars as pl


# Copp_v3 by zhengk
def signal(df, n, factor_name, config):
    # COPP indicator
    """
    RC=100*((CLOSE-REF(CLOSE,N1))/REF(CLOSE,N1)+(CLOSE-REF(CLOSE,N2))/REF(CLOSE,N2))
    COPP=WMA(RC,M)
    The COPP indicator uses a weighted moving average of price rate-of-change over different time lengths to measure
    momentum. If COPP crosses above/below 0, it generates a buy/sell signal.
    """
    df = df.with_columns(
        pl.Series(
            "RC",
            100
            * (
                (df["close"] - df["close"].shift(n)) / (df["close"].shift(n) + config.eps)
                + (df["close"] - df["close"].shift(int(1.618 * n))) / (df["close"].shift(int(1.618 * n)) + config.eps)
            ),
        )
    )
    df = df.with_columns(pl.Series(factor_name, df["RC"].rolling_mean(n, min_samples=config.min_periods)))

    df = df.drop("RC")

    return df
