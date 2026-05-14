import numpy as np


def signal(df, n, factor_name, config):
    # Cmo
    eps = config.eps
    # MAX(CLOSE-REF(CLOSE,1), 0
    df["max_su"] = np.where(df["close"] > df["close"].shift(1), df["close"] - df["close"].shift(1), 0)
    # SU=SUM(MAX(CLOSE-REF(CLOSE,1),0),N)
    df["sum_su"] = df["max_su"].rolling(n, min_periods=config.min_periods).sum()
    # MAX(REF(CLOSE,1)-CLOSE,0)
    df["max_sd"] = np.where(df["close"].shift(1) > df["close"], df["close"].shift(1) - df["close"], 0)
    # SD=SUM(MAX(REF(CLOSE,1)-CLOSE,0),N)
    df["sum_sd"] = df["max_sd"].rolling(n, min_periods=config.min_periods).sum()
    # CMO=(SU-SD)/(SU+SD)*100
    df[factor_name] = (df["sum_su"] - df["sum_sd"]) / (df["sum_su"] + df["sum_sd"] + eps) * 100

    # delete extra columns
    del df["max_su"], df["sum_su"], df["max_sd"], df["sum_sd"]

    return df
