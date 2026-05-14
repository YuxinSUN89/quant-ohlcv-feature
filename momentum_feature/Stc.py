import numpy as np


def signal(df, n, factor_name, config):
    # STC indicator
    """
    N1=23
    N2=50
    N=40
    MACDX=EMA(CLOSE,N1)-EMA(CLOSE,N2)
    V1=MIN(MACDX,N)
    V2=MAX(MACDX,N)-V1
    FK=IF(V2>0,(MACDX-V1)/V2*100,REF(FK,1))
    FD=SMA(FK,N,1)
    V3=MIN(FD,N)
    V4=MAX(FD,N)-V3
    SK=IF(V4>0,(FD-V3)/V4*100,REF(SK,1))
    STC=SD=SMA(SK,N,1)
    STC combines the algorithms of MACD and KDJ. First it computes MACD from the difference
    between short and long moving averages, then computes fast stochastic FK and FD of MACD,
    and finally computes the slow stochastic SK and SD of MACD. The slow stochastic is the STC.
    STC can reflect overbought/oversold conditions. Generally, STC > 75 is overbought, STC < 25 is oversold.
    A buy signal is generated when STC crosses above 25;
    a sell signal is generated when STC crosses below 75.
    """
    N1 = n
    N2 = int(N1 * 1.5)  # approximate value
    N = 2 * n
    # Numerical sensitivity note:
    # STC stacks EMA, rolling min/max, and recursive fallback (REF(previous FK/SK)).
    # Tiny floating-point differences can therefore accumulate into small output drift,
    # even when the overall shape is matched between pandas and polars.
    df["ema1"] = df["close"].ewm(span=N1, adjust=config.ewm_adjust).mean()
    df["ema2"] = df["close"].ewm(span=N, adjust=config.ewm_adjust).mean()
    df["MACDX"] = df["ema1"] - df["ema2"]
    df["V1"] = df["MACDX"].rolling(N2, min_periods=config.min_periods).min()
    df["V2"] = df["MACDX"].rolling(N2, min_periods=config.min_periods).max() - df["V1"]
    df["FK"] = (df["MACDX"] - df["V1"]) / df["V2"] * 100
    df["FK"] = np.where(df["V2"] > 0, (df["MACDX"] - df["V1"]) / df["V2"] * 100, df["FK"].shift(1))
    df["FD"] = df["FK"].rolling(N2, min_periods=config.min_periods).mean()
    df["V3"] = df["FD"].rolling(N2, min_periods=config.min_periods).min()
    df["V4"] = df["FD"].rolling(N2, min_periods=config.min_periods).max() - df["V3"]
    df["SK"] = (df["FD"] - df["V3"]) / df["V4"] * 100
    df["SK"] = np.where(df["V4"] > 0, (df["FD"] - df["V3"]) / df["V4"] * 100, df["SK"].shift(1))
    df[factor_name] = df["SK"].rolling(N1, min_periods=config.min_periods).mean()

    del df["ema1"]
    del df["ema2"]
    del df["MACDX"]
    del df["V1"]
    del df["V2"]
    del df["V3"]
    del df["V4"]
    del df["FK"]
    del df["FD"]
    del df["SK"]

    return df
