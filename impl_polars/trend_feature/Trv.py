import polars as pl


def signal(df, n, factor_name, config):
    # Trv indicator (Rolling percentage change of Moving Average)
    # Formula: MA = MA(CLOSE,N); TRV = 100 * (MA - REF(MA,N)) / REF(MA,N)
    #          result = MA(TRV, N)
    # Measures the smoothed N-period rate of change of the moving average.
    # Captures the velocity of the trend rather than the raw price movement.
    # calculate volatility factor
    df = df.with_columns(pl.Series("ma", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("trv", 100 * ((df["ma"] - df["ma"].shift(n)) / (df["ma"] + config.eps).shift(n))))
    df = df.with_columns(pl.Series(factor_name, df["trv"].rolling_mean(n, min_samples=config.min_periods)))

    drop_col = ["ma", "trv"]
    df = df.drop(drop_col)

    return df
