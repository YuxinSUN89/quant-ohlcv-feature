from impl_pandas.helpers import scale_01


def signal(df, n, factor_name, config):
    # Ma indicator (Moving Average, 0-1 normalized)
    # Formula: MA = MA(CLOSE, N); result = scale_01(MA, N, config.normalize_eps, config=config)
    # Computes the rolling mean of close price and normalizes to [0,1] within its rolling range.
    # Values near 1 indicate MA is near its recent high; values near 0 indicate near its recent low.
    s = df["close"].rolling(n, min_periods=config.min_periods).mean()
    df[factor_name] = scale_01(s, n, config.normalize_eps, config=config)

    return df
