import numpy as np


def signal(df, n, factor_name, config):
    eps = config.eps
    #  WAD indicator
    """
    TRH=MAX(HIGH,REF(CLOSE,1))
    TRL=MIN(LOW,REF(CLOSE,1))
    AD=IF(CLOSE>REF(CLOSE,1),CLOSE-TRL,CLOSE-TRH)
    AD=IF(CLOSE==REF(CLOSE,1),0,AD)
    WAD=CUMSUM(AD)
    N=20
    WADMA=MA(WAD,N)
    Reference: https://zhidao.baidu.com/question/19720557.html
    If today's close > yesterday's close, A/D = close minus the smaller of yesterday's close and today's low;
    If today's close < yesterday's close, A/D = close minus the larger of yesterday's close and today's high;
    If today's close == yesterday's close, A/D = 0;
    WAD = cumulative sum of A/D from the first trading day;
    """
    df["ref_close"] = df["close"].shift(1)
    df["TRH"] = df[["high", "ref_close"]].max(axis=1)
    df["TRL"] = df[["low", "ref_close"]].min(axis=1)
    df["AD"] = np.where(df["close"] > df["close"].shift(1), df["close"] - df["TRL"], df["close"] - df["TRH"])
    df["AD"] = np.where(df["close"] == df["close"].shift(1), 0, df["AD"])
    df["WAD"] = df["AD"].cumsum()
    df["WADMA"] = df["WAD"].rolling(n, min_periods=config.min_periods).mean()
    # normalize
    df[factor_name] = df["WAD"] / (df["WADMA"] + eps)

    del df["ref_close"]
    del df["TRH"], df["TRL"]
    del df["AD"]
    del df["WAD"]
    del df["WADMA"]

    return df
