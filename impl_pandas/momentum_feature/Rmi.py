import numpy as np


def signal(df, n, factor_name, config):
    # RMI indicator
    """
    N=7
    RMI=SMA(MAX(CLOSE-REF(CLOSE,4),0),N,1)/SMA(ABS(CLOSE-REF(CLOSE,1)),N,1)*100
    RMI is similar to RSI in calculation, but replaces the momentum term CLOSE-REF(CLOSE,1)
    with the difference from four days ago: CLOSE-REF(CLOSE,4).
    """
    df["max_close"] = np.where(df["close"] > df["close"].shift(4), df["close"] - df["close"].shift(4), 0)
    df["abs_close"] = df["close"] - df["close"].shift(1)
    df["sma_1"] = df["max_close"].rolling(n, min_periods=config.min_periods).mean()
    df["sma_2"] = df["abs_close"].rolling(n, min_periods=config.min_periods).mean()
    df[factor_name] = df["sma_1"] / df["sma_2"] * 100

    del df["max_close"]
    del df["abs_close"]
    del df["sma_1"]
    del df["sma_2"]

    return df
