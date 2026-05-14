import polars as pl


def signal(df, n, factor_name, config):
    # AmplitudeMax indicator (Rolling maximum candle amplitude)
    # Formula: AMPLITUDE = MAX(|HIGH/OPEN - 1|, |LOW/OPEN - 1|); result = ROLLING_MAX(AMPLITUDE, N)
    # Measures the maximum single-candle price swing (as a fraction of open) over N periods.
    # Captures the largest intrabar move, useful for detecting outlier volatility events.
    amp1 = (df["high"] / df["open"] - 1).abs()
    amp2 = (df["low"] / df["open"] - 1).abs()
    df = df.with_columns(hourly_amplitude=pl.max_horizontal([amp1, amp2]))
    df = df.with_columns(pl.Series(factor_name, df["hourly_amplitude"].rolling_max(n, min_samples=config.min_periods)))
    df = df.drop("hourly_amplitude")

    return df
