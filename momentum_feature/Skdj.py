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
    df["RSV"] = (
        (df["close"] - df["low"].rolling(n, min_periods=config.min_periods).min())
        / (
            df["high"].rolling(n, min_periods=config.min_periods).max()
            - df["low"].rolling(n, min_periods=config.min_periods).min()
        )
        * 100
    )
    df["MARSV"] = df["RSV"].ewm(com=2, adjust=config.ewm_adjust).mean()

    df["K"] = df["MARSV"].ewm(com=2, adjust=config.ewm_adjust).mean()
    df[factor_name] = df["K"].rolling(3, min_periods=config.min_periods).mean()

    del df["RSV"]
    del df["MARSV"]
    del df["K"]

    return df
