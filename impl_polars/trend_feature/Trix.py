import polars as pl


def signal(df, n, factor_name, config):
    # Trix indicator (Triple EMA rate of change)
    # Formula: EMA1 = EMA(CLOSE,N); EMA2 = EMA(EMA1,N); EMA3 = EMA(EMA2,N)
    #          result = (EMA3 - REF(EMA3,1)) / (REF(EMA3,1) + eps)
    # TRIX filters out short-term noise via triple smoothing, then measures its 1-period % change.
    # Positive values signal upward momentum in the triple-smoothed trend; negative signal downward.
    eps = config.eps
    df = df.with_columns(pl.Series("ema", df["close"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("ema_ema", df["ema"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("ema_ema_ema", df["ema_ema"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    # TRIX=(TRIPLE_EMA-REF(TRIPLE_EMA,1))/REF(TRIPLE_EMA,1)
    df = df.with_columns(
        pl.Series(factor_name, (df["ema_ema_ema"] - df["ema_ema_ema"].shift(1)) / (df["ema_ema_ema"].shift(1) + eps))
    )

    # remove redundant columns
    df = df.drop(["ema", "ema_ema", "ema_ema_ema"])

    return df
