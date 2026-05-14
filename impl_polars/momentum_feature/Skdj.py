import polars as pl


def signal(df, n, factor_name, config):
    # SKDJ indicator
    """
    N=60
    M=5
    RSV=(CLOSE-MIN(LOW,N))/(MAX(HIGH,N)-MIN(LOW,N))*100
    MARSV=SMA(RSV,3,1)
    K=SMA(MARSV,3,1)
    D=MA(K,3)
    SKDJ is the Slow Stochastic Oscillator (i.e., Slow KDJ). K in SKDJ corresponds to D in KDJ,
    and D in SKDJ is the moving average of D in KDJ. Usage is the same as KDJ.
    Buy when D < 40 (oversold) and K crosses above D; sell when D > 60 (overbought) and K crosses below D.
    """
    df = df.with_columns(
        pl.Series(
            "RSV",
            (df["close"] - df["low"].rolling_min(n, min_samples=config.min_periods))
            / (
                df["high"].rolling_max(n, min_samples=config.min_periods)
                - df["low"].rolling_min(n, min_samples=config.min_periods)
            )
            * 100,
        )
    )
    df = df.with_columns(pl.Series("MARSV", df["RSV"].ewm_mean(com=2, adjust=config.ewm_adjust)))

    df = df.with_columns(pl.Series("K", df["MARSV"].ewm_mean(com=2, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series(factor_name, df["K"].rolling_mean(3, min_samples=config.min_periods)))

    df = df.drop("RSV")
    df = df.drop("MARSV")
    df = df.drop("K")

    return df
