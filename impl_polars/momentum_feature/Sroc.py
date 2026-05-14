import polars as pl


def signal(df, n, factor_name, config):
    # Sroc
    eps = config.eps
    """
    N=13
    M=21
    EMAP=EMA(CLOSE,N)
    SROC=(EMAP-REF(EMAP,M))/REF(EMAP,M)
    SROC is similar to ROC, but smooths the closing price before computing the rate of change.
    """
    ema = df["close"].ewm_mean(span=n, adjust=config.ewm_adjust)
    ref = ema.shift(2 * n)
    df = df.with_columns(pl.Series(factor_name, (ema - ref) / (ref + eps)))

    return df
