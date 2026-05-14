def signal(df, n, factor_name, config):
    # Tema indicator
    eps = config.eps
    """
    N=20,40
    TEMA=3*EMA(CLOSE,N)-3*EMA(EMA(CLOSE,N),N)+EMA(EMA(EMA(CLOSE,N),N),N)
    TEMA combines single, double and triple EMAs, with less lag than ordinary moving averages.
    We use crossings of fast and slow TEMA to generate trading signals.
    """
    df["ema"] = df["close"].ewm(span=n, adjust=config.ewm_adjust).mean()  # EMA(CLOSE,N)
    df["ema_ema"] = df["ema"].ewm(span=n, adjust=config.ewm_adjust).mean()  # EMA(EMA(CLOSE,N),N)
    df["ema_ema_ema"] = df["ema_ema"].ewm(span=n, adjust=config.ewm_adjust).mean()  # EMA(EMA(EMA(CLOSE,N),N),N)
    # TEMA=3*EMA(CLOSE,N)-3*EMA(EMA(CLOSE,N),N)+EMA(EMA(EMA(CLOSE,N),N),N)
    df["TEMA"] = 3 * df["ema"] - 3 * df["ema_ema"] + df["ema_ema_ema"]
    # normalize
    df[factor_name] = df["ema"] / (df["TEMA"] + eps) - 1

    return df
