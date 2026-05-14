from impl_pandas.helpers import scale_01


def signal(df, n, factor_name, config):
    # MaSignal indicator (Close - MA, 0-1 normalized)
    # Formula: result = scale_01(CLOSE - MA(CLOSE, N, config.normalize_eps), N, config=config)
    # Measures the deviation of close from its MA, normalized to [0,1].
    # Values above 0.5 indicate close is above the MA; below 0.5 indicates below the MA.
    s = df["close"] - df["close"].rolling(n, min_periods=config.min_periods).mean()
    df[factor_name] = scale_01(s, n, config.normalize_eps, config=config)

    return df
