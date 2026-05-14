import numpy as np


def signal(df, n, factor_name, config):
    # IMI indicator
    """
    N=14
    INC=SUM(IF(CLOSE>OPEN,CLOSE-OPEN,0),N)
    DEC=SUM(IF(OPEN>CLOSE,OPEN-CLOSE,0),N)
    IMI=INC/(INC+DEC)
    IMI is calculated similarly to RSI. The difference is that IMI uses
    close price and open price, while RSI uses close price and the previous day's close price.
    So RSI compares two consecutive days, while IMI compares within the same trading day.
    If IMI crosses above 80, a buy signal is generated; if IMI crosses below 20, a sell signal is generated.
    """
    df["INC"] = np.where(df["close"] > df["open"], df["close"] - df["open"], 0)
    df["INC_sum"] = df["INC"].rolling(n, min_periods=config.min_periods).sum()
    df["DEC"] = np.where(df["open"] > df["close"], df["open"] - df["close"], 0)
    df["DEC_sum"] = df["DEC"].rolling(n, min_periods=config.min_periods).sum()
    df[factor_name] = df["INC_sum"] / (df["INC_sum"] + df["DEC_sum"])

    del df["INC"]
    del df["INC_sum"]
    del df["DEC"]
    del df["DEC_sum"]

    return df
