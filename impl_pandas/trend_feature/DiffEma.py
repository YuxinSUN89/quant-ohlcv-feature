def signal(df, n, factor_name, config):
    # DiffEma indicator (Short EMA - Long EMA relative to its own EMA)
    # Formula: DIFF_EMA = EMA(CLOSE,N) - EMA(CLOSE,3N)
    #          result = DIFF_EMA / EMA(DIFF_EMA, N) - 1
    # Measures how the EMA spread (short minus long) compares to its own recent average.
    # Positive values indicate the spread is widening (accelerating trend); negative indicates narrowing (decelerating).
    short_windows = n
    long_windows = 3 * n
    df["ema_short"] = df["close"].ewm(span=short_windows, adjust=config.ewm_adjust).mean()
    df["ema_long"] = df["close"].ewm(span=long_windows, adjust=config.ewm_adjust).mean()
    df["diff_ema"] = df["ema_short"] - df["ema_long"]

    df["diff_ema_mean"] = df["diff_ema"].ewm(span=n, adjust=config.ewm_adjust).mean()

    df[factor_name] = df["diff_ema"] / df["diff_ema_mean"] - 1

    del df["ema_short"]
    del df["ema_long"]
    del df["diff_ema"]
    del df["diff_ema_mean"]

    return df
