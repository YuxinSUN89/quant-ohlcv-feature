def signal(df, n, factor_name, config):
    # MtmMax indicator (MTM vs rolling max of MTM)
    # Formula: MTM = CLOSE/REF(CLOSE,N)-1; result = MTM - MAX(MTM, N).shift(1)
    # Measures how the current N-period momentum compares to the maximum momentum achieved over the past N periods.
    # Negative values indicate current momentum is below recent peak (momentum fading); 0 indicates new high.
    df["mtm"] = df["close"] / (df["close"].shift(n) + config.eps) - 1
    df["up"] = df["mtm"].rolling(window=n, min_periods=config.min_periods).max().shift(1)
    df[factor_name] = df["mtm"] - df["up"]

    return df
