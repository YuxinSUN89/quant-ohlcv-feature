def signal(df, n, factor_name, config):
    # KdjD indicator (KDJ D line)
    # Formula: RSV = (CLOSE - MIN(LOW,N)) / (MAX(HIGH,N) - MIN(LOW,N)) * 100
    #          K = EWM(RSV, com=2);  D = EWM(K, com=2)
    # The D line of the KDJ oscillator — a double smoothing of the raw stochastic (RSV).
    # D is smoother than K and used for signal confirmation. Overbought > 80; oversold < 20.
    eps = config.eps
    low_list = (
        df["low"].rolling(n, min_periods=config.min_periods).min()
    )  # MIN(LOW,N) find minimum low within the period
    high_list = (
        df["high"].rolling(n, min_periods=config.min_periods).max()
    )  # MAX(HIGH,N) find maximum high within the period
    # Stochastics=(CLOSE-LOW_N)/(HIGH_N-LOW_N)*100 calculate a stochastic value
    rsv = (df["close"] - low_list) / (high_list - low_list + eps) * 100
    # K D J values are within a fixed range
    df["K"] = rsv.ewm(com=2, adjust=config.ewm_adjust).mean()  # K=SMA(Stochastics,3,1) calculate K
    df[factor_name] = df["K"].ewm(com=2, adjust=config.ewm_adjust).mean()  # D=SMA(K,3,1) calculate D

    # remove redundant columns
    del df["K"]

    return df
