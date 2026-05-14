import numpy as np


def signal(df, n, factor_name, config):
    # Adx+mtm indicator (DI+ directional strength × EMA-smoothed momentum)
    # Formula: PDM = positive directional movement (high gain only when larger than low gain)
    #          DI+ = SUM(PDM,N) / SUM(TR,N)  (positive directional indicator)
    #          MTM = MA(CLOSE/REF(CLOSE,N) - 1, N)  (rolling mean of N-period returns)
    #          result = DI+ * MTM
    # Composite of upward directional strength (DI+) and price momentum.
    # High positive values indicate strong upward trend with sustained momentum.
    df["max_high"] = np.where(df["high"] > df["high"].shift(1), df["high"] - df["high"].shift(1), 0)

    df["max_low"] = np.where(df["low"].shift(1) > df["low"], df["low"].shift(1) - df["low"], 0)
    df["XPDM"] = np.where(df["max_high"] > df["max_low"], df["high"] - df["high"].shift(1), 0)
    df["PDM"] = df["XPDM"].rolling(n, min_periods=config.min_periods).sum()

    df["c1"] = abs(df["high"] - df["low"])
    df["c2"] = abs(df["high"] - df["close"])
    df["c3"] = abs(df["low"] - df["close"])
    df["TR"] = df[["c1", "c2", "c3"]].max(axis=1)

    df["TR_sum"] = df["TR"].rolling(n, min_periods=config.min_periods).sum()
    df["DI+"] = df["PDM"] / df["TR_sum"]

    df["mtm"] = (df["close"] / df["close"].shift(n) - 1).rolling(window=n, min_periods=config.min_periods).mean()

    df[factor_name] = df["DI+"] * df["mtm"]

    del df["max_high"]
    del df["max_low"]
    del df["XPDM"]
    del df["PDM"]
    del df["mtm"]
    del df["c1"]
    del df["c2"]
    del df["c3"]
    del df["TR"]
    del df["TR_sum"]
    del df["DI+"]

    return df
