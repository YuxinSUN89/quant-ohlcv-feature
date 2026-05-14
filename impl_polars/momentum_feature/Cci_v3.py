import polars as pl


def signal(df, n, factor_name, config):
    # Cci_v3 indicator (CCI using all four OHLC EMA-smoothed prices)
    # Formula: TP = (EMA(O,N) + EMA(H,N) + EMA(L,N) + EMA(C,N)) / 4
    #          MA = EMA(TP, N); MD = EMA(|EMA(C,N) - MA|, N)
    #          result = (TP - MA) / (MD + eps)
    # A variant of CCI using all four OHLC prices EMA-smoothed as the typical price.
    # Uses EMA-based mean deviation for smoother response compared to standard CCI.
    eps = config.eps
    oma = df["open"].ewm_mean(span=n, adjust=config.ewm_adjust)
    hma = df["high"].ewm_mean(span=n, adjust=config.ewm_adjust)
    lma = df["low"].ewm_mean(span=n, adjust=config.ewm_adjust)
    cma = df["close"].ewm_mean(span=n, adjust=config.ewm_adjust)
    tp = (oma + hma + lma + cma) / 4
    ma = tp.ewm_mean(span=n, adjust=config.ewm_adjust)
    md = (cma - ma).abs().ewm_mean(span=n, adjust=config.ewm_adjust)
    df = df.with_columns(pl.Series(factor_name, (tp - ma) / (md + eps)))

    return df
