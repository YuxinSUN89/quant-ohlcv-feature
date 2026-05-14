from impl_pandas.helpers import scale_01


def signal(df, n, factor_name, config):
    # Mac_v5 indicator (MAC using (rolling high + rolling low + open)/3)
    # Formula: PRICE = (MAX(HIGH,N) + MIN(LOW,N) + OPEN) / 3
    #          MAC = 10 * (MA(PRICE,N) - MA(PRICE,2N)); result = scale_01(MAC,N, config.normalize_eps, config=config)
    # Uses a modified price that replaces close with open, alongside rolling high/low extremes.
    high = df["high"].rolling(n, min_periods=config.min_periods).max()
    low = df["low"].rolling(n, min_periods=config.min_periods).min()
    _open = df["open"]

    ma_short = ((high + low + _open) / 3.0).rolling(n, min_periods=config.min_periods).mean()
    ma_long = ((high + low + _open) / 3.0).rolling(2 * n, min_periods=config.min_periods).mean()

    _mac = 10 * (ma_short - ma_long)
    df[factor_name] = scale_01(_mac, n, config.normalize_eps, config=config)

    return df
