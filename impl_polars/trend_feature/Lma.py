import polars as pl


def signal(df, n, factor_name, config):
    # LMA indicator
    """
    N=20
    LMA=MA(LOW,N)
    LMA is a simple moving average with the closing price replaced by the lowest price.
    Buy/sell signals are generated when the low crosses above/below LMA.
    """
    df = df.with_columns(pl.Series("low_ma", df["low"].rolling_mean(n, min_samples=config.min_periods)))
    # normalize
    df = df.with_columns(pl.Series(factor_name, df["low"] / df["low_ma"] - 1))

    df = df.drop("low_ma")

    return df
