def signal(df, n, factor_name, config):
    # Bias indicator (Price deviation from MA)
    # Formula: BIAS = CLOSE / MA(CLOSE, N) - 1
    # Measures how far the close price deviates from its N-period moving average as a percentage.
    # Positive values indicate price is above MA (overbought potential); negative values indicate below MA (oversold potential).
    df["ma"] = df["close"].rolling(n, min_periods=config.min_periods).mean()
    df[factor_name] = df["close"] / (df["ma"] + config.eps) - 1

    del df["ma"]

    return df
