import polars as pl


def signal(df, n, factor_name, config):
    # Pac indicator
    eps = config.eps
    """
    N1=20
    N2=20
    UPPER=SMA(HIGH,N1,1)
    LOWER=SMA(LOW,N2,1)
    Construct a price channel using moving averages of high and low prices.
    Go long if price breaks above the upper band; go short if it breaks below the lower band.
    """
    df = df.with_columns(pl.Series("upper", df["high"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("lower", df["low"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("width", df["upper"] - df["lower"]))
    df = df.with_columns(pl.Series("width_ma", df["width"].rolling_mean(n, min_samples=config.min_periods)))

    df = df.with_columns(pl.Series(factor_name, df["width"] / (df["width_ma"] + eps) - 1))

    # remove redundant columns
    df = df.drop(["upper", "lower", "width", "width_ma"])

    return df
