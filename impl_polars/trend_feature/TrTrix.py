import polars as pl


def signal(df, n, factor_name, config):
    # TrTrix indicator (single EMA percentage change)
    # Formula: EMA1 = EMA(CLOSE,N); result = EMA1.pct_change()
    # Simplified variant of TRIX using only a single EMA layer.
    # Measures the 1-period rate of change of the EMA, capturing short-term trend momentum.
    df = df.with_columns(pl.Series("tr_trix", df["close"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series(factor_name, df["tr_trix"].pct_change()))

    # remove redundant columns
    df = df.drop("tr_trix")

    return df
