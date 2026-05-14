def signal(df, n, factor_name, config):
    # Qstick indicator
    """
    N=20
    Qstick=MA(CLOSE-OPEN,N)
    Qstick reflects the direction and strength of price trends by comparing closing and opening prices.
    Buy/sell signals are generated when Qstick crosses above/below 0.
    """
    cl = df["close"] - df["open"]
    # Numerical sensitivity note:
    # Qstick can explode when the rolling mean of (close-open) is extremely close to zero.
    # Small signed floating residuals can therefore lead to very large finite values.
    Qstick = cl.rolling(n, min_periods=config.min_periods).mean()
    # normalize
    df[factor_name] = cl / Qstick - 1

    return df
