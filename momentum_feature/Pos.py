def signal(df, n, factor_name, config):
    # POS indicator
    """
    N=100
    PRICE=(CLOSE-REF(CLOSE,N))/REF(CLOSE,N)
    POS=(PRICE-MIN(PRICE,N))/(MAX(PRICE,N)-MIN(PRICE,N))
    POS measures where the current N-day return falls between the maximum and minimum
    N-day returns over the past N days. A buy signal is generated when POS crosses above 80;
    a sell signal is generated when POS crosses below 20.

    """
    ref = df["close"].shift(n)
    price = (df["close"] - ref) / ref
    min_price = price.rolling(n, min_periods=config.min_periods).min()
    max_price = price.rolling(n, min_periods=config.min_periods).max()
    df[factor_name] = (price - min_price) / (max_price - min_price)

    return df
