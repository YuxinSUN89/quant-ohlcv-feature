def signal(df, n, factor_name, config):
    # Cv indicator
    eps = config.eps
    """
    N=10
    H_L_EMA=EMA(HIGH-LOW,N)
    CV=(H_L_EMA-REF(H_L_EMA,N))/REF(H_L_EMA,N)*100
    The CV indicator measures stock price volatility, reflecting the rate of change of the difference
    between high and low prices (amplitude) over a period. If the absolute value of CV crosses below 30, buy;
    if the absolute value of CV crosses above 70, sell.
    """
    # H_L_EMA=EMA(HIGH-LOW,N)
    df["H_L_ema"] = (df["high"] - df["low"]).ewm(span=n, adjust=config.ewm_adjust).mean()
    df[factor_name] = (df["H_L_ema"] - df["H_L_ema"].shift(n)) / (df["H_L_ema"].shift(n) + eps) * 100

    del df["H_L_ema"]

    return df
