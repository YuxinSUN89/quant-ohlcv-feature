import polars as pl


def signal(df, n, factor_name, config):
    # ZLMACD indicator
    """
    N1=20
    N2=100
    ZLMACD=(2*EMA(CLOSE,N1)-EMA(EMA(CLOSE,N1),N1))-(2*EM
    A(CLOSE,N2)-EMA(EMA(CLOSE,N2),N2))
    ZLMACD is an improvement on the MACD indicator that uses DEMA instead of EMA in its
    calculation, overcoming the lag of the MACD indicator. A buy/sell signal is generated
    when ZLMACD crosses above/below 0.
    """
    ema1 = df["close"].ewm_mean(span=n, adjust=config.ewm_adjust)
    ema_ema_1 = ema1.ewm_mean(span=n, adjust=config.ewm_adjust)
    n2 = 5 * n
    ema2 = df["close"].ewm_mean(span=n2, adjust=config.ewm_adjust)
    ema_ema_2 = ema2.ewm_mean(span=n2, adjust=config.ewm_adjust)
    ZLMACD = (2 * ema1 - ema_ema_1) - (2 * ema2 - ema_ema_2)
    df = df.with_columns(pl.Series(factor_name, df["close"] / ZLMACD - 1))

    return df
