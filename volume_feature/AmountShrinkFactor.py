def signal(*args):
    # AmountShrinkFactor indicator (short vs. long traded-value level ratio)
    # Formula: AmountShrinkFactor = n-day mean of QUOTE_VOLUME / m-day mean of QUOTE_VOLUME, where n < m
    # Ratio of an n-day quote-volume average to a longer 3n-day quote-volume average.
    # Below 1 signals recent trading value is running below its longer-term baseline — a volume-drying-up setup.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    short = int(n)
    long = int(20)
    short_mean = df['quote_volume'].rolling(short).mean()
    long_mean = df['quote_volume'].rolling(long).mean()
    df[factor_name] = short_mean / long_mean

    return df
