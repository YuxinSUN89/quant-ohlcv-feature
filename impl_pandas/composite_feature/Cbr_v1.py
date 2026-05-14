import talib as ta


def signal(df, n, factor_name, config):
    # Cbr_v1 indicator (COPP × BBW × price-volume correlation composite)
    # Formula: RC = 100 * (CLOSE_CHANGE_N/CLOSE_N + CLOSE_CHANGE_2N/CLOSE_2N); COPP = MA(RC, N)
    #          BBW = STD(CLOSE,N) / MA(CLOSE,N); CORR = CORREL(CLOSE, VOLUME, N) + 1
    #          CBR = COPP * BBW * MA(CORR, N)
    # Combines the Coppock curve (dual-window momentum) with Bollinger bandwidth (volatility)
    # and close-volume correlation. Higher values suggest trending momentum with high volatility
    # and price-volume alignment.

    # Copp
    df["RC"] = 100 * (
        (df["close"] - df["close"].shift(n)) / (df["close"].shift(n) + config.eps)
        + (df["close"] - df["close"].shift(2 * n)) / (df["close"].shift(2 * n) + config.eps)
    )
    df["RC"] = df["RC"].rolling(n, min_periods=config.min_periods).mean()

    # bbw
    df["median"] = df["close"].rolling(n, min_periods=config.min_periods).mean()
    df["std"] = df["close"].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
    df["bbw"] = df["std"] / (df["median"] + config.eps)

    # corr
    df["corr"] = ta.CORREL(df["close"], df["volume"], n) + 1
    df["corr"] = df["corr"].rolling(n, min_periods=config.min_periods).mean()

    df[factor_name] = df["RC"] * df["bbw"] * df["corr"]

    del df["RC"], df["median"], df["std"], df["bbw"], df["corr"]

    return df
