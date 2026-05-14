import polars as pl


def signal(df, n, factor_name, config):
    # Dema indicator
    eps = config.eps
    """
    N=60
    EMA=EMA(CLOSE,N)
    DEMA=2*EMA-EMA(EMA,N)
    DEMA combines single EMA and double EMA to reduce lag while maintaining smoothness.
    """
    ema = df["close"].ewm_mean(span=n, adjust=config.ewm_adjust)  # EMA=EMA(CLOSE,N)
    ema_ema = ema.ewm_mean(span=n, adjust=config.ewm_adjust)  # EMA(EMA,N)
    dema = 2 * ema - ema_ema  # DEMA=2*EMA-EMA(EMA,N)
    # normalize dema
    df = df.with_columns(pl.Series(factor_name, dema / (ema + eps) - 1))

    return df
