from impl_pandas.helpers import scale_01


def signal(df, n, factor_name, config):
    # ******************** Expma ********************
    # N1=12
    # N2=50
    # EMA1=EMA(CLOSE,N1)
    # EMA2=EMA(CLOSE,N2)
    # Exponential Moving Average is an improved version of the Simple Moving Average, designed to reduce the lag problem.
    ema1 = df["close"].ewm(span=n, min_periods=config.min_periods, adjust=config.ewm_adjust).mean()
    ema2 = df["close"].ewm(span=(4 * n), min_periods=config.min_periods, adjust=config.ewm_adjust).mean()

    s = ema1 - ema2
    df[factor_name] = scale_01(s, n, config.normalize_eps, config=config)

    return df
