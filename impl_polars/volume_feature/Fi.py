import polars as pl


def signal(df, n, factor_name, config):
    # Fi indicator (Force Index, z-score normalized with EMA smoothing)
    # Formula: FI = VOLUME * (CLOSE - REF(CLOSE, 1))
    #          FI_ZSCORE = (FI - MA(FI,N)) / STD(FI,N); result = EMA(FI_ZSCORE, N)
    # Force Index quantifies buying/selling force by combining price change magnitude with volume.
    # Z-score normalization removes scale effects; EMA smoothing reduces noise.
    # Positive values indicate sustained upward force; negative values indicate downward force.
    eps = config.eps
    _fi = df["volume"] * (df["close"] - df["close"].shift(1))
    _fi_zscore = (_fi - _fi.rolling_mean(n, min_samples=config.min_periods)) / (
        _fi.rolling_std(n, min_samples=config.min_periods, ddof=config.ddof) + eps
    )
    s = _fi_zscore.ewm_mean(span=n, adjust=config.ewm_adjust)
    df = df.with_columns(pl.Series(factor_name, s))

    return df
