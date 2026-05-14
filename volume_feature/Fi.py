import pandas as pd


def signal(df, n, factor_name, config):
    # Fi indicator (Force Index, z-score normalized with EMA smoothing)
    # Formula: FI = VOLUME * (CLOSE - REF(CLOSE, 1))
    #          FI_ZSCORE = (FI - MA(FI,N)) / STD(FI,N); result = EMA(FI_ZSCORE, N)
    # Force Index quantifies buying/selling force by combining price change magnitude with volume.
    # Z-score normalization removes scale effects; EMA smoothing reduces noise.
    # Positive values indicate sustained upward force; negative values indicate downward force.
    eps = config.eps
    _fi = df["volume"] * (df["close"] - df["close"].shift(1))
    _fi_zscore = (_fi - _fi.rolling(n, min_periods=config.min_periods).mean()) / (
        _fi.rolling(n, min_periods=config.min_periods).std(ddof=config.ddof) + eps
    )
    s = _fi_zscore.ewm(span=n, adjust=config.ewm_adjust, min_periods=config.min_periods).mean()
    df[factor_name] = pd.Series(s)

    return df
