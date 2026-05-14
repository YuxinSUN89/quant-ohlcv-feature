import polars as pl


def signal(df, n, factor_name, config):
    # MagicCci_v2 indicator (CCI using HLC average as typical price, EWM-based)
    # Formula: TP = (EMA(H,N) + EMA(L,N) + EMA(C,N)) / 3
    #          MA = EMA(TP, N); MD = EMA(|TP - MA|, N)
    #          result = (TP - MA) / MD
    # A variant of CCI using only HLC (no open) EWM-smoothed as the typical price.
    # Note: when using this indicator, n cannot be greater than half the number of filtered candles (not half the number of fetched candles)
    # df['oma'] = df['open'].ewm_mean(span=n, adjust=config.ewm_adjust)
    df = df.with_columns(pl.Series("hma", df["high"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("lma", df["low"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("cma", df["close"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("tp", (df["hma"] + df["lma"] + df["cma"]) / 3))
    df = df.with_columns(pl.Series("ma", df["tp"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("abs_diff_close", abs(df["tp"] - df["ma"])))
    df = df.with_columns(pl.Series("md", df["abs_diff_close"].ewm_mean(span=n, adjust=config.ewm_adjust)))

    df = df.with_columns(pl.Series(factor_name, (df["tp"] - df["ma"]) / df["md"]))

    # # delete intermediate data
    # del df['oma']
    df = df.drop("hma")
    df = df.drop("lma")
    df = df.drop("cma")
    df = df.drop("tp")
    df = df.drop("ma")
    df = df.drop("abs_diff_close")
    df = df.drop("md")

    return df
