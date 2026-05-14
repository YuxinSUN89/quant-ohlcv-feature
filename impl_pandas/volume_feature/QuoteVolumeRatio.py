def signal(df, n, factor_name, config):
    # QuoteVolumeRatio indicator
    # Formula: result = QUOTE_VOLUME / MA(QUOTE_VOLUME, N)
    # Measures the current quote volume relative to its rolling mean over N periods.
    # Values > 1 indicate above-average trading activity; values < 1 indicate below-average activity.
    df[factor_name] = df["quote_volume"] / (df["quote_volume"].rolling(n, min_periods=config.min_periods).mean() + config.eps)

    return df
