import polars as pl


def signal(df, n, factor_name, config):
    # MAAMT indicator
    """
    N=40
    MAAMT=MA(AMOUNT,N)
    MAAMT is a moving average of trading volume. Buy/sell signals are generated
    when volume crosses above/below the moving average.
    """
    MAAMT = df["volume"].rolling_mean(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series(factor_name, (df["volume"] - MAAMT) / MAAMT))  # avoid dimensionality issues

    return df
