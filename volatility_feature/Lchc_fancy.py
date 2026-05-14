def signal(df, n, factor_name, config):
    # Ratio of current price to the highest and lowest prices over the past N minutes, checking whether upward or downward momentum is stronger
    df[factor_name] = (
        -1 * df["low"].rolling(n, min_periods=config.min_periods).min() / df["close"]
        - df["high"].rolling(n, min_periods=config.min_periods).max() / df["close"]
    )

    return df
