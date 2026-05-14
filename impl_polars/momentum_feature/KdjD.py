import polars as pl


def signal(df, n, factor_name, config):
    # KdjD indicator (KDJ D line)
    # Formula: RSV = (CLOSE - MIN(LOW,N)) / (MAX(HIGH,N) - MIN(LOW,N)) * 100
    #          K = EWM(RSV, com=2);  D = EWM(K, com=2)
    # The D line of the KDJ oscillator — a double smoothing of the raw stochastic (RSV).
    # D is smoother than K and used for signal confirmation. Overbought > 80; oversold < 20.
    eps = config.eps
    low_list = df["low"].rolling_min(n, min_samples=config.min_periods)  # MIN(LOW,N) find minimum low within the period
    high_list = df["high"].rolling_max(
        n, min_samples=config.min_periods
    )  # MAX(HIGH,N) find maximum high within the period
    # Stochastics=(CLOSE-LOW_N)/(HIGH_N-LOW_N)*100 calculate a stochastic value
    rsv = (df["close"] - low_list) / (high_list - low_list + eps) * 100
    # K D J values are within a fixed range
    df = df.with_columns(
        pl.Series("K", rsv.ewm_mean(com=2, adjust=config.ewm_adjust))
    )  # K=SMA(Stochastics,3,1) calculate K
    df = df.with_columns(
        pl.Series(factor_name, df["K"].ewm_mean(com=2, adjust=config.ewm_adjust))
    )  # D=SMA(K,3,1) calculate D

    # remove redundant columns
    df = df.drop("K")

    return df
