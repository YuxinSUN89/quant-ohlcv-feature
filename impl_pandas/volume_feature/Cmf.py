def signal(df, n, factor_name, config):
    # CMF indicator
    """
    N=60
    CMF=SUM(((CLOSE-LOW)-(HIGH-CLOSE))*VOLUME/(HIGH-LOW),N)/SUM(VOLUME,N)
    CMF weights volume using CLV. If the close price is above the midpoint of high and low,
    the volume is positive (buying power dominates); if the close price is below the midpoint,
    the volume is negative (selling power dominates).
    If CMF crosses above 0, a buy signal is generated;
    if CMF crosses below 0, a sell signal is generated.
    """
    A = ((df["close"] - df["low"]) - (df["high"] - df["close"])) * df["volume"] / (df["high"] - df["low"])
    df[factor_name] = (
        A.rolling(n, min_periods=config.min_periods).sum()
        / (df["volume"].rolling(n, min_periods=config.min_periods).sum() + config.eps)
    )

    return df
