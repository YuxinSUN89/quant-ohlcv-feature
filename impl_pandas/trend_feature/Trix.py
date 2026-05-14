def signal(df, n, factor_name, config):
    # Trix indicator (Triple EMA rate of change)
    # Formula: EMA1 = EMA(CLOSE,N); EMA2 = EMA(EMA1,N); EMA3 = EMA(EMA2,N)
    #          result = (EMA3 - REF(EMA3,1)) / (REF(EMA3,1) + eps)
    # TRIX filters out short-term noise via triple smoothing, then measures its 1-period % change.
    # Positive values signal upward momentum in the triple-smoothed trend; negative signal downward.
    eps = config.eps
    df["ema"] = df["close"].ewm(span=n, adjust=config.ewm_adjust).mean()  # EMA(CLOSE,N)
    df["ema_ema"] = df["ema"].ewm(span=n, adjust=config.ewm_adjust).mean()  # EMA(EMA(CLOSE,N),N)
    df["ema_ema_ema"] = df["ema_ema"].ewm(span=n, adjust=config.ewm_adjust).mean()  # EMA(EMA(EMA(CLOSE,N),N),N)
    # TRIX=(TRIPLE_EMA-REF(TRIPLE_EMA,1))/REF(TRIPLE_EMA,1)
    df[factor_name] = (df["ema_ema_ema"] - df["ema_ema_ema"].shift(1)) / (df["ema_ema_ema"].shift(1) + eps)

    # remove redundant columns
    del df["ema"], df["ema_ema"], df["ema_ema_ema"]

    return df
