def signal(df, n, factor_name, config):
    # Bias_v11 indicator (Volume-weighted Bias with EMA smoothing)
    # Formula: BIAS = CLOSE/MA(CLOSE,N) - 1; VOL_RATIO = QUOTE_VOLUME / MA(QUOTE_VOLUME,N)
    #          MTM = BIAS * VOL_RATIO; result = EMA(MTM, N)
    # Volume-weighted price bias: amplifies signal when above-average volume accompanies the price deviation.
    # EMA smoothing reduces noise. High positive values indicate volume-backed upside momentum.
    df["ma"] = df["close"].rolling(n, min_periods=config.min_periods).mean()
    df["mtm"] = (
        (df["close"] / (df["ma"] + config.eps) - 1)
        * df["quote_volume"]
        / (df["quote_volume"].rolling(n, min_periods=config.min_periods).mean() + config.eps)
    )
    # EMA
    df[factor_name] = df["mtm"].ewm(span=n, adjust=config.ewm_adjust).mean()

    del df["ma"], df["mtm"]

    return df
