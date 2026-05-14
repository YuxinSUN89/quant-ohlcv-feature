import polars as pl


def signal(df, n, factor_name, config):
    # MagicCci indicator (CCI using OHLC average as typical price, EWM-based)
    # Formula: TP = (EMA(O,N) + EMA(H,N) + EMA(L,N) + EMA(C,N)) / 4
    #          MA = EMA(TP, N); MD = EMA(|TP - MA|, N)
    #          result = (TP - MA) / (MD + eps)
    # Uses all four OHLC prices EWM-smoothed to compute a robust CCI variant.
    # Note: when using this indicator, n must not exceed half the number of filtered candles (not half the number of fetched candles)
    eps = config.eps
    df = df.with_columns(pl.Series("oma", df["open"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("hma", df["high"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("lma", df["low"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("cma", df["close"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("tp", (df["oma"] + df["hma"] + df["lma"] + df["cma"]) / 4))
    df = df.with_columns(pl.Series("ma", df["tp"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("abs_diff_close", abs(df["tp"] - df["ma"])))
    df = df.with_columns(pl.Series("md", df["abs_diff_close"].ewm_mean(span=n, adjust=config.ewm_adjust)))

    df = df.with_columns(pl.Series(factor_name, (df["tp"] - df["ma"]) / (df["md"] + eps)))

    # # remove intermediate data
    df = df.drop("oma")
    df = df.drop("hma")
    df = df.drop("lma")
    df = df.drop("cma")
    df = df.drop("tp")
    df = df.drop("ma")
    df = df.drop("abs_diff_close")
    df = df.drop("md")

    return df
