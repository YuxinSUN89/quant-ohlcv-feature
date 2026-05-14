def signal(df, n, factor_name, config):
    # KDJD indicator
    """
    N=20
    M=60
    LOW_N=MIN(LOW,N)
    HIGH_N=MAX(HIGH,N)
    Stochastics=(CLOSE-LOW_N)/(HIGH_N-LOW_N)*100
    Stochastics_LOW=MIN(Stochastics,M)
    Stochastics_HIGH=MAX(Stochastics,M)
    Stochastics_DOUBLE=(Stochastics-Stochastics_LOW)/(Stochastics_HIGH-Stochastics_LOW)*100
    K=SMA(Stochastics_DOUBLE,3,1)
    D=SMA(K,3,1)
    KDJD can be seen as a variant of KDJ. The variable Stochastics in the KDJ calculation
    measures where the closing price falls between the highest and lowest prices over the
    past N days. The Stochastics_DOUBLE in the KDJD calculation measures where Stochastics
    falls between its maximum and minimum values over the past N days. Here it is used as
    a momentum indicator. Buy/sell signals are generated when D crosses above 70 / below 30.
    """
    min_low = df["low"].rolling(n, min_periods=config.min_periods).min()
    max_high = df["high"].rolling(n, min_periods=config.min_periods).max()
    Stochastics = (df["close"] - min_low) / (max_high - min_low) * 100
    Stochastics_LOW = Stochastics.rolling(n * 3, min_periods=config.min_periods).min()
    Stochastics_HIGH = Stochastics.rolling(n * 3, min_periods=config.min_periods).max()
    Stochastics_DOUBLE = (Stochastics - Stochastics_LOW) / (Stochastics_HIGH - Stochastics_LOW)
    K = Stochastics_DOUBLE.ewm(com=2, adjust=config.ewm_adjust).mean()  # K
    df[factor_name] = K.ewm(com=2, adjust=config.ewm_adjust).mean()  # D

    return df
