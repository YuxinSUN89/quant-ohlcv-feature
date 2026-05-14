import polars as pl


def signal(df, n, factor_name, config):
    # KdjJ indicator (KDJ J line)
    # Formula: RSV = (CLOSE - MIN(LOW,N)) / (MAX(HIGH,N) - MIN(LOW,N)) * 100
    #          K = EWM(RSV, com=2); D = EWM(K, com=2); J = 3K - 2D
    # The J line of KDJ amplifies divergence between K and D lines.
    # J can exceed [0, 100] and is more sensitive to reversals than K or D alone.
    eps = config.eps
    low_list = df["low"].rolling_min(n, min_samples=config.min_periods)  # MIN(LOW,N) find minimum low within the period
    high_list = df["high"].rolling_max(
        n, min_samples=config.min_periods
    )  # MAX(HIGH,N) find maximum high within the period
    # Stochastics=(CLOSE-LOW_N)/(HIGH_N-LOW_N)*100 calculate a stochastic value
    rsv = (df["close"] - low_list) / (high_list - low_list + eps) * 100
    # K D J values are within a fixed range
    df = df.with_columns(pl.Series("K", rsv.ewm_mean(com=2, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("D", df["K"].ewm_mean(com=2, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series(factor_name, 3 * df["K"] - 2 * df["D"]))

    # remove redundant columns
    df = df.drop(["K", "D"])

    return df
