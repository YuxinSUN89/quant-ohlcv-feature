import numpy as np


def signal(df, n, factor_name, config):
    """
    N=40
    AV=IF(CLOSE>REF(CLOSE,1),AMOUNT,0)
    BV=IF(CLOSE<REF(CLOSE,1),AMOUNT,0)
    CV=IF(CLOSE=REF(CLOSE,1),AMOUNT,0)
    AVS=SUM(AV,N)
    BVS=SUM(BV,N)
    CVS=SUM(CV,N)
    VRAMT=(AVS+CVS/2)/(BVS+CVS/2)
    VRAMT is calculated the same as the VR indicator (Volume Ratio), but replaces
    trading volume with trading amount.
    A buy signal is generated when VRAMT crosses above 180;
    a sell signal is generated when VRAMT crosses below 70.
    """
    eps = config.eps
    df["AV"] = np.where(df["close"] > df["close"].shift(1), df["volume"], 0)  # AV=IF(CLOSE>REF(CLOSE,1),AMOUNT,0)
    df["BV"] = np.where(df["close"] < df["close"].shift(1), df["volume"], 0)  # BV=IF(CLOSE<REF(CLOSE,1),AMOUNT,0)
    df["CV"] = np.where(df["close"] == df["close"].shift(1), df["volume"], 0)  # CV=IF(CLOSE=REF(CLOSE,1),AMOUNT,0)
    df["AVS"] = df["AV"].rolling(n, min_periods=config.min_periods).sum()  # AVS=SUM(AV,N)
    df["BVS"] = df["BV"].rolling(n, min_periods=config.min_periods).sum()  # BVS=SUM(BV,N)
    df["CVS"] = df["CV"].rolling(n, min_periods=config.min_periods).sum()  # CVS=SUM(CV,N)
    df[factor_name] = (df["AVS"] + df["CVS"] / 2) / (df["BVS"] + df["CVS"] / 2 + eps)  # VRAMT=(AVS+CVS/2)/(BVS+CVS/2)

    del df["AV"]
    del df["BV"]
    del df["CV"]
    del df["AVS"]
    del df["BVS"]
    del df["CVS"]

    return df
