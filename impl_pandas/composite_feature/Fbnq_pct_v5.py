def signal(df, n, factor_name, config):
    # Fbnq_pct_v5 indicator (Fibonacci multi-period momentum × volatility composite)
    # Formula: FBNQ_MEAN = mean of EMA(CLOSE, pn) for pn in [5,8,13,21,34,55,89]; momentum = FBNQ_MEAN.pct_change(N)
    #          BBW = mean of STD(CLOSE,N)/MA(CLOSE,N) for pn in [5,8,13,21,34,55,89]
    #          result = momentum * BBW
    # Uses Fibonacci numbers as EMA periods to capture multi-scale trend momentum,
    # then multiplies by the average Bollinger bandwidth to scale momentum by market volatility.
    # Positive values indicate trending upward momentum with elevated volatility.
    params = [5, 8, 13, 21, 34, 55, 89]
    df["Fbnq_mean"] = 0
    df["BbwOri"] = 0
    for pn in params:
        # momentum
        df["Fbnq_mean"] += df["close"].ewm(span=pn, adjust=config.ewm_adjust).mean()
        # volatility
        df["BbwOri"] += (
            df["close"].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
            / df["close"].rolling(n, min_periods=config.min_periods).mean()
        )
    # momentum
    df["Fbnq_mean"] = df["Fbnq_mean"] / len(params)
    df["Fbnq_mean"] = df["Fbnq_mean"].pct_change(n)

    # volatility
    df["BbwOri"] = df["BbwOri"] / len(params)

    # momentum * volatility
    df[factor_name] = df["Fbnq_mean"] * df["BbwOri"]
    del df["Fbnq_mean"], df["BbwOri"]

    return df
