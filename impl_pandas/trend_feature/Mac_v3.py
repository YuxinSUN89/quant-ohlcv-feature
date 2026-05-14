from impl_pandas.helpers import scale_01


def signal(df, n, factor_name, config):
    # Mac_v3 indicator (MAC using rolling max/min midpoint)
    # Formula: PRICE = (MAX(HIGH,N) + MIN(LOW,N))/2
    #          MAC = 10 * (MA(PRICE,N) - MA(PRICE,2N)); result = scale_01(MAC,N, config.normalize_eps, config=config)
    # MAC computed on the rolling high-low midpoint, capturing the channel center rather than the candle midpoint.
    high = df["high"].rolling(n, min_periods=config.min_periods).max()
    low = df["low"].rolling(n, min_periods=config.min_periods).min()

    ma_short = (0.5 * high + 0.5 * low).rolling(n, min_periods=config.min_periods).mean()
    ma_long = (0.5 * high + 0.5 * low).rolling(2 * n, min_periods=config.min_periods).mean()

    _mac = 10 * (ma_short - ma_long)
    df[factor_name] = scale_01(_mac, n, config.normalize_eps, config=config)

    return df
