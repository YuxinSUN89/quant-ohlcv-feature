from impl_pandas.helpers import scale_01


def signal(df, n, factor_name, config):
    # Mac_v4 indicator (MAC using typical price with rolling extremes)
    # Formula: PRICE = (MAX(HIGH,N) + MIN(LOW,N) + CLOSE) / 3
    #          MAC = 10 * (MA(PRICE,N) - MA(PRICE,2N)); result = scale_01(MAC,N, config.normalize_eps, config=config)
    # Uses a modified typical price that includes rolling high/low extremes plus current close.
    high = df["high"].rolling(n, min_periods=config.min_periods).max()
    low = df["low"].rolling(n, min_periods=config.min_periods).min()
    close = df["close"]

    ma_short = ((high + low + close) / 3.0).rolling(n, min_periods=config.min_periods).mean()
    ma_long = ((high + low + close) / 3.0).rolling(2 * n, min_periods=config.min_periods).mean()

    _mac = 10 * (ma_short - ma_long)
    df[factor_name] = scale_01(_mac, n, config.normalize_eps, config=config)

    return df
