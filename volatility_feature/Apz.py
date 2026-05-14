def signal(df, n, factor_name, config):
    """
    N=10
    M=20
    PARAM=2
    VOL=EMA(EMA(HIGH-LOW,N),N)
    UPPER=EMA(EMA(CLOSE,M),M)+PARAM*VOL
    LOWER= EMA(EMA(CLOSE,M),M)-PARAM*VOL
    APZ (Adaptive Price Zone) is similar to Bollinger Bands and the Keltner Channel:
    all are price channels built around a moving average based on price volatility.
    The difference lies in how volatility is measured: Bollinger Bands use the standard
    deviation of the close, the Keltner Channel uses the true range ATR, and APZ uses
    the N-day double exponential average of the high-low difference to measure price amplitude.
    """
    df["hl"] = df["high"] - df["low"]
    df["ema_hl"] = df["hl"].ewm(span=n, adjust=config.ewm_adjust).mean()
    df["vol"] = df["ema_hl"].ewm(span=n, adjust=config.ewm_adjust).mean()

    # calculate the channel; can be used as a CTA strategy or adapted as a factor
    df["ema_close"] = df["close"].ewm(span=2 * n, adjust=config.ewm_adjust).mean()
    df["ema_ema_close"] = df["ema_close"].ewm(span=2 * n, adjust=config.ewm_adjust).mean()
    # normalize using EMA
    df[factor_name] = df["vol"] / df["ema_ema_close"]

    del df["hl"]
    del df["ema_hl"]
    del df["vol"]
    del df["ema_close"]
    del df["ema_ema_close"]

    return df
