import polars as pl


def signal(df, n, factor_name, config):
    # AvgPrice indicator (VWAP normalized within rolling range)
    # Formula: VWAP = SUM(QUOTE_VOLUME,N) / SUM(VOLUME,N)
    #          result = (VWAP - MIN(VWAP,N)) / (MAX(VWAP,N) - MIN(VWAP,N) + eps)
    # Computes a rolling VWAP (volume-weighted average price) and normalizes it to [0,1]
    # within its N-period range. Values near 1 indicate VWAP is near its recent high; near 0 near its low.
    eps = config.eps
    df = df.with_columns(
        pl.Series(
            "price",
            df["quote_volume"].rolling_sum(n, min_samples=config.min_periods)
            / (df["volume"].rolling_sum(n, min_samples=config.min_periods) + config.eps),
        )
    )
    df = df.with_columns(
        pl.Series(
            factor_name,
            (df["price"] - df["price"].rolling_min(n, min_samples=config.min_periods))
            / (
                df["price"].rolling_max(n, min_samples=config.min_periods)
                - df["price"].rolling_min(n, min_samples=config.min_periods)
                + eps
            ),
        )
    )

    # remove redundant columns
    df = df.drop("price")

    return df
