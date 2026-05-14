import numpy as np


def signal(df, n, factor_name, config):
    # Demaker indicator
    """
    N=20
    Demax=HIGH-REF(HIGH,1)
    Demax=IF(Demax>0,Demax,0)
    Demin=REF(LOW,1)-LOW
    Demin=IF(Demin>0,Demin,0)
    Demaker=MA(Demax,N)/(MA(Demax,N)+MA(Demin,N))
    When Demaker>0.7, the uptrend is strong; when Demaker<0.3, the downtrend is strong.
    When Demaker crosses above 0.7 / crosses below 0.3, a buy/sell signal is generated.
    """
    df["Demax"] = df["high"] - df["high"].shift(1)
    df["Demax"] = np.where(df["Demax"] > 0, df["Demax"], 0)
    df["Demin"] = df["low"].shift(1) - df["low"]
    df["Demin"] = np.where(df["Demin"] > 0, df["Demin"], 0)
    df["Demax_ma"] = df["Demax"].rolling(n, min_periods=config.min_periods).mean()
    df["Demin_ma"] = df["Demin"].rolling(n, min_periods=config.min_periods).mean()
    df[factor_name] = df["Demax_ma"] / (df["Demax_ma"] + df["Demin_ma"])

    del df["Demax"]
    del df["Demin"]
    del df["Demax_ma"]
    del df["Demin_ma"]

    return df
