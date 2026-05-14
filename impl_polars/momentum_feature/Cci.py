import polars as pl


def signal(df, n, factor_name, config):
    # CCI - most commonly used T indicator
    eps = config.eps
    """
    N=14
    TP=(HIGH+LOW+CLOSE)/3
    MA=MA(TP,N)
    MD=MA(ABS(TP-MA),N)
    CCI=(TP-MA)/(0.015MD)
    The CCI indicator measures the deviation of the typical price (mean of high, low, and close) from its moving average over a period.
    CCI can be used to reflect overbought and oversold market conditions.
    Generally, CCI above 100 indicates the market is overbought; CCI below -100 indicates the market is oversold.
    When CCI crosses below 100 / crosses above -100, it suggests the price may begin to reverse, and one may consider selling/buying.
    """

    df = df.with_columns(pl.Series("tp", (df["high"] + df["low"] + df["close"]) / 3))
    df = df.with_columns(pl.Series("ma", df["tp"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("md", abs(df["tp"] - df["ma"]).rolling_mean(n, min_samples=config.min_periods)))

    df = df.with_columns(pl.Series(factor_name, (df["tp"] - df["ma"]) / (df["md"] * 0.015 + eps)))

    df = df.drop("tp")
    df = df.drop("ma")
    df = df.drop("md")

    return df
