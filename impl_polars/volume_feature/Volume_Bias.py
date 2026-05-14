import polars as pl


# Volume_Bias indicator (short-term vs long-term volume ratio)
# Formula: result = MA(QUOTE_VOLUME, N/24) / MA(QUOTE_VOLUME, N) - 1
# Compares recent short-window (N/24) average volume to the longer N-period average.
# Positive values indicate a recent volume surge relative to the longer baseline (heightened activity).
def signal(df, n, factor_name, config):
    short_window = max(n // 24, 1)
    df = df.with_columns(
        pl.Series(
            factor_name,
            df["quote_volume"].rolling_mean(short_window, min_samples=config.min_periods)
            / df["quote_volume"].rolling_mean(n, min_samples=config.min_periods)
            - 1,
        )
    )

    return df
