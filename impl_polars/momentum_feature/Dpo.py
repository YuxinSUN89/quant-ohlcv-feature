import polars as pl


def signal(df, n, factor_name, config):
    # Dpo
    eps = config.eps
    """
    N=20
    DPO=CLOSE-REF(MA(CLOSE,N),N/2+1)
    DPO is the difference between the current price and a lagged moving average,
    reducing the influence of long-term trends on short-term price fluctuations by removing a prior moving average.
    DPO>0 indicates the current market is bullish;
    DPO<0 indicates the current market is bearish.
    We use DPO crossing above/below 0 to generate buy/sell signals.
    """

    df = df.with_columns(pl.Series("median", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(
        pl.Series(factor_name, (df["close"] - df["median"].shift(int(n / 2) + 1)) / (df["median"] + eps))
    )

    df = df.drop("median")

    return df
