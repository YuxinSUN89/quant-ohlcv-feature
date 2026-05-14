def signal(df, n, factor_name, config):
    # IC
    """
    N1=9
    N2=26
    N3=52
    TS=(MAX(HIGH,N1)+MIN(LOW,N1))/2
    KS=(MAX(HIGH,N2)+MIN(LOW,N2))/2
    SPAN_A=(TS+KS)/2
    SPAN_B=(MAX(HIGH,N3)+MIN(LOW,N3))/2
    In the IC indicator, the area between SPAN_A and SPAN_B is called the cloud. If the price is
    above the cloud, it indicates an uptrend (if SPAN_A>SPAN_B, the uptrend is strong;
    otherwise the uptrend is weak); if the price is below the cloud, it indicates a downtrend (if
    SPAN_A<SPAN_B, the downtrend is strong; otherwise the downtrend is weak). This indicator
    is used similarly to moving averages, such as the faster line (TS) crossing
    the slower line (KS), price breaking through KS, price breaking through the cloud, SPAN_A breaking through SPAN_B,
    etc. Our signal generation: if price is above the cloud and SPAN_A>SPAN_B,
    buy when price crosses above KS; if price is below the cloud and SPAN_A<SPAN_B,
    sell when price crosses below KS.
    """
    n2 = 3 * n
    n3 = 2 * n2
    df["max_high_1"] = df["high"].rolling(n, min_periods=config.min_periods).max()
    df["min_low_1"] = df["low"].rolling(n, min_periods=config.min_periods).min()
    df["TS"] = (df["max_high_1"] + df["min_low_1"]) / 2
    df["max_high_2"] = df["high"].rolling(n2, min_periods=config.min_periods).max()
    df["min_low_2"] = df["low"].rolling(n2, min_periods=config.min_periods).min()
    df["KS"] = (df["max_high_2"] + df["min_low_2"]) / 2
    df["span_A"] = (df["TS"] + df["KS"]) / 2
    df["max_high_3"] = df["high"].rolling(n3, min_periods=config.min_periods).max()
    df["min_low_3"] = df["low"].rolling(n3, min_periods=config.min_periods).min()
    df["span_B"] = (df["max_high_3"] + df["min_low_3"]) / 2

    # normalize/remove dimensionality
    df[factor_name] = df["span_A"] / df["span_B"]

    del df["max_high_1"]
    del df["max_high_2"]
    del df["max_high_3"]
    del df["min_low_1"]
    del df["min_low_2"]
    del df["min_low_3"]
    del df["TS"]
    del df["KS"]
    del df["span_A"]
    del df["span_B"]

    return df
