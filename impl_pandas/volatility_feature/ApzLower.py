from impl_pandas.helpers import scale_01


def signal(df, n, factor_name, config):
    # ApzLower indicator
    """
    N=10
    M=20
    PARAM=2
    VOL=EMA(EMA(HIGH-LOW,N),N)
    UPPER=EMA(EMA(CLOSE,M),M)+PARAM*VOL
    LOWER= EMA(EMA(CLOSE,M),M)-PARAM*VOL
    ApzLower (Adaptive Price Zone) is similar to Bollinger Bands and the Keltner Channel:
    all are price channels built around a moving average based on price volatility.
    The difference lies in how volatility is measured: Bollinger Bands use the standard
    deviation of the close, the Keltner Channel uses the true range ATR, and ApzLower uses
    the N-day double exponential average of the high-low difference to measure price amplitude.
    """
    vol = (
        (df["high"] - df["low"])
        .ewm(span=n, adjust=config.ewm_adjust, min_periods=config.min_periods)
        .mean()
        .ewm(span=n, adjust=config.ewm_adjust, min_periods=config.min_periods)
        .mean()
    )
    upper = (
        df["close"]
        .ewm(span=int(2 * n), adjust=config.ewm_adjust, min_periods=config.min_periods)
        .mean()
        .ewm(span=int(2 * n), adjust=config.ewm_adjust, min_periods=config.min_periods)
        .mean()
        + 2 * vol
    )

    s = upper - 4 * vol
    df[factor_name] = scale_01(s, n, config.normalize_eps, config=config)

    return df
