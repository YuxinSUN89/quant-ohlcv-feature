import pandas as pd


def signal(df, n, factor_name, config):
    # Ic_v2 indicator (IC indicator: close position relative to SpanA/SpanB cloud)
    # Formula: TS = (MAX(HIGH,N) + MIN(LOW,N))/2; KS = (MAX(HIGH,2N) + MIN(LOW,2N))/2
    #          SPAN_A = (TS + KS)/2; SPAN_B = (MAX(HIGH,3N) + MIN(LOW,3N))/2
    #          result = (CLOSE - SPAN_B) / (SPAN_A - SPAN_B)
    # Based on Ichimoku Cloud components. Measures where close sits relative to the cloud boundaries.
    # Values above 1 = above cloud (bullish); below 0 = below cloud (bearish); 0-1 = inside cloud.
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
    s = (df["close"] - span_b) / (config.normalize_eps + span_a - span_b)

    df[factor_name] = pd.Series(s)

    return df
