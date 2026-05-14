import numpy as np


def signal(df, n, factor_name, config):
    # Rsi
    eps = config.eps
    """
    CLOSEUP=IF(CLOSE>REF(CLOSE,1),CLOSE-REF(CLOSE,1),0)
    CLOSEDOWN=IF(CLOSE<REF(CLOSE,1),ABS(CLOSE-REF(CLOSE,1)),0)
    CLOSEUP_MA=SMA(CLOSEUP,N,1)
    CLOSEDOWN_MA=SMA(CLOSEDOWN,N,1)
    RSI=100*CLOSEUP_MA/(CLOSEUP_MA+CLOSEDOWN_MA)
    RSI reflects the ratio of average gains to average losses over a period.
    When RSI > 70, the market is considered to be in a strong uptrend or even overbought;
    when RSI < 30, the market is in a strong downtrend or even oversold.
    When RSI drops below 30 then crosses back above 30, prices are expected to rebound from oversold levels;
    when RSI exceeds 70 then crosses below 70, the market is expected to pull back from overbought levels.
    In practice, the 70/30 threshold is not required. Here we use 60/40 as signal thresholds.
    A buy signal is generated when RSI crosses above 40; a sell signal when RSI crosses below 60.
    """

    diff = df["close"].diff()  # CLOSE-REF(CLOSE,1) calculate difference between current close and previous period close
    # IF(CLOSE>REF(CLOSE,1),CLOSE-REF(CLOSE,1),0) record upward move when price is rising
    df["up"] = np.where(diff > 0, diff, 0)
    # IF(CLOSE<REF(CLOSE,1),ABS(CLOSE-REF(CLOSE,1)),0) record downward move when price is falling
    df["down"] = np.where(diff < 0, abs(diff), 0)
    A = (
        df["up"].ewm(span=n, adjust=config.ewm_adjust).mean()
    )  # SMA(CLOSEUP,N,1) calculate sma of upward moves in the period
    B = (
        df["down"].ewm(span=n, adjust=config.ewm_adjust).mean()
    )  # SMA(CLOSEDOWN,N,1) calculate sma of downward moves in the period
    # RSI=100*CLOSEUP_MA/(CLOSEUP_MA+CLOSEDOWN_MA)  omit multiplication by 100 for normalization
    df[factor_name] = A / (A + B + eps)

    # remove redundant columns
    del df["up"], df["down"]

    return df
