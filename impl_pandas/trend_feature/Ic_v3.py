from impl_pandas.helpers import scale_01


def signal(df, n, factor_name, config):
    # Ic_v3 indicator (Ichimoku SpanA - SpanB cloud thickness, 0-1 normalized)
    # Formula: TS = (MAX(HIGH,N) + MIN(LOW,N))/2; KS = (MAX(HIGH,2N) + MIN(LOW,2N))/2
    #          SPAN_A = (TS + KS)/2; SPAN_B = (MAX(HIGH,3N) + MIN(LOW,3N))/2
    #          result = scale_01(SPAN_A - SPAN_B, N, config.normalize_eps, config=config)
    # Measures the thickness of the Ichimoku cloud (SpanA - SpanB), normalized to [0,1].
    # Positive values indicate SpanA > SpanB (bullish cloud); negative indicates bearish cloud.
    high_max1 = df["high"].rolling(n, min_periods=config.min_periods).max()
    high_max2 = df["high"].rolling(int(2 * n), min_periods=config.min_periods).max()
    high_max3 = df["high"].rolling(int(3 * n), min_periods=config.min_periods).max()
    low_min1 = df["low"].rolling(n, min_periods=config.min_periods).min()
    low_min2 = df["low"].rolling(int(2 * n), min_periods=config.min_periods).min()
    low_min3 = df["low"].rolling(int(3 * n), min_periods=config.min_periods).min()
    ts = (high_max1 + low_min1) / 2.0
    ks = (high_max2 + low_min2) / 2.0
    span_a = (ts + ks) / 2.0
    span_b = (high_max3 + low_min3) / 2.0

    s = span_a - span_b
    df[factor_name] = scale_01(s, n, config.normalize_eps, config=config)

    return df
