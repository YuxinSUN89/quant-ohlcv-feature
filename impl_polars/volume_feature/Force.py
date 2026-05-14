import polars as pl


def signal(df, n, factor_name, config):
    # Force indicator (quote-volume force index relative to its rolling mean)
    # Formula: FORCE = QUOTE_VOLUME * (CLOSE - REF(CLOSE,1)); result = FORCE / MA(FORCE, N)
    # Combines price change direction/magnitude with quote volume to measure buying/selling force.
    # Values > 1 indicate current force is above its N-period average (strong momentum); < 1 below average.
    # Note: n should not exceed half the number of filtered K-lines when using this indicator (not half the K-line data fetched)
    df = df.with_columns(pl.Series("force", df["quote_volume"] * (df["close"] - df["close"].shift(1))))
    df = df.with_columns(
        pl.Series(factor_name, df["force"] / df["force"].rolling_mean(n, min_samples=config.min_periods))
    )

    # ref = ma.shift(n)  # MADisplaced=REF(MA_CLOSE,M)

    df = df.drop("force")

    return df
