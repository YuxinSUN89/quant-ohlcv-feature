import polars as pl


def signal(df, n, factor_name, config):
    # Cse indicator (Time-series normalized close, EMA smoothed)
    # Formula: CLOSE_STD = (CLOSE - MIN(CLOSE,N)) / (MAX(CLOSE,N) - MIN(CLOSE,N))
    #          result = EMA(CLOSE_STD, N-1)
    # Normalizes close price to [0,1] within its rolling range, then smooths with EMA.
    # Values near 1 indicate close is near the top of its N-period range (bullish); near 0 indicates bottom.

    # time-series normalization
    close_min = df["close"].rolling_min(n, min_samples=config.min_periods)
    close_max = df["close"].rolling_max(n, min_samples=config.min_periods)
    close_standard = (df["close"] - close_min) / (close_max - close_min)
    # exponential moving average
    df = df.with_columns(pl.Series(factor_name, close_standard.ewm_mean(span=n - 1, adjust=config.ewm_adjust)))

    return df
