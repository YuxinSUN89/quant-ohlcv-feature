def signal(*args):
    # AmountShrinkVol indicator (short vs. long traded-value volatility ratio)
    # Formula: AmountShrinkVol = n-day std of QUOTE_VOLUME / m-day std of QUOTE_VOLUME, where n < m
    # Ratio of an n-day quote-volume std to an m-day (longer) quote-volume std, where n < m.
    # Below 1 signals trading-value volatility is contracting relative to its longer-term level — a classic pre-breakout 'shrinking volume' setup.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    short = int(n)
    long = int(20)
    short_std = df['quote_volume'].rolling(short).std()
    long_std = df['quote_volume'].rolling(long).std()
    df[factor_name] = short_std / long_std

    return df
