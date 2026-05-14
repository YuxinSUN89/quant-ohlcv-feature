from impl_pandas.helpers import scale_01


def signal(df, n, factor_name, config):
    # EnvUpper indicator (Envelope upper band, 0-1 normalized)
    # Formula: UPPER = MA(CLOSE, N) * (1 + 0.05); result = scale_01(UPPER, N, config.normalize_eps, config=config)
    # Computes the upper band of an Envelope channel (MA ± 5%) and normalizes to [0,1].
    # Envelope channels are used to identify overbought/oversold levels relative to a percentage
    # offset from the moving average.
    upper = (1 + 0.05) * df["close"].rolling(n, min_periods=config.min_periods).mean()

    s = upper
    df[factor_name] = scale_01(s, n, config.normalize_eps, config=config)

    return df
