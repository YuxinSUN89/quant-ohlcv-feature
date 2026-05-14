# Volume_Bias indicator (short-term vs long-term volume ratio)
# Formula: result = MA(QUOTE_VOLUME, N/24) / MA(QUOTE_VOLUME, N) - 1
# Compares recent short-window (N/24) average volume to the longer N-period average.
# Positive values indicate a recent volume surge relative to the longer baseline (heightened activity).
def signal(df, n, factor_name, config):
    short_n = max(1, n // 24)
    df[factor_name] = (
        df["quote_volume"].rolling(short_n, min_periods=config.min_periods).mean()
        / (df["quote_volume"].rolling(n, min_periods=config.min_periods).mean() + config.eps)
        - 1
    )

    return df
