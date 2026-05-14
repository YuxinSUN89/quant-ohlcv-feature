def signal(df, n, factor_name, config):
    # DC indicator
    """
    N=20
    UPPER=MAX(HIGH,N)
    LOWER=MIN(LOW,N)
    MIDDLE=(UPPER+LOWER)/2
    The DC indicator uses the N-period highest price and N-period lowest price to construct upper and lower price channels,
    then takes their average as the middle channel. A buy/sell signal is generated when the close price crosses above/below the middle channel.
    """
    upper = df["high"].rolling(n, min_periods=config.min_periods).max()
    lower = df["low"].rolling(n, min_periods=config.min_periods).min()
    middle = (upper + lower) / 2
    width = upper - lower
    # normalize (remove units)
    df[factor_name] = width / middle

    return df
