def signal(df, n, factor_name, config):
    # Cci_v3 indicator (CCI using all four OHLC EMA-smoothed prices)
    # Formula: TP = (EMA(O,N) + EMA(H,N) + EMA(L,N) + EMA(C,N)) / 4
    #          MA = EMA(TP, N); MD = EMA(|EMA(C,N) - MA|, N)
    #          result = (TP - MA) / (MD + eps)
    # A variant of CCI using all four OHLC prices EMA-smoothed as the typical price.
    # Uses EMA-based mean deviation for smoother response compared to standard CCI.
    eps = config.eps
    oma = df["open"].ewm(span=n, adjust=config.ewm_adjust).mean()
    hma = df["high"].ewm(span=n, adjust=config.ewm_adjust).mean()
    lma = df["low"].ewm(span=n, adjust=config.ewm_adjust).mean()
    cma = df["close"].ewm(span=n, adjust=config.ewm_adjust).mean()
    tp = (oma + hma + lma + cma) / 4
    ma = tp.ewm(span=n, adjust=config.ewm_adjust).mean()
    md = (cma - ma).abs().ewm(span=n, adjust=config.ewm_adjust).mean()
    df[factor_name] = (tp - ma) / (md + eps)

    return df
