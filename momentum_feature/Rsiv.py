import numpy as np


def signal(df, n, factor_name, config):
    # RSIV indicator
    """
    N=20
    VOLUP=IF(CLOSE>REF(CLOSE,1),VOLUME,0)
    VOLDOWN=IF(CLOSE<REF(CLOSE,1),VOLUME,0)
    SUMUP=SUM(VOLUP,N)
    SUMDOWN=SUM(VOLDOWN,N)
    RSIV=100*SUMUP/(SUMUP+SUMDOWN)
    RSIV is calculated like RSI, but the price change CLOSE-REF(CLOSE,1) is replaced
    with volume VOLUME. Usage is similar to RSI. Here we use it as a momentum indicator;
    buy when it crosses above 60, sell when it crosses below 40.
    """
    df["VOLUP"] = np.where(df["close"] > df["close"].shift(1), df["volume"], 0)
    df["VOLDOWN"] = np.where(df["close"] < df["close"].shift(1), df["volume"], 0)
    df["SUMUP"] = df["VOLUP"].rolling(n, min_periods=config.min_periods).sum()
    df["SUMDOWN"] = df["VOLDOWN"].rolling(n, min_periods=config.min_periods).sum()
    df[factor_name] = df["SUMUP"] / (df["SUMUP"] + df["SUMDOWN"]) * 100

    del df["VOLUP"]
    del df["VOLDOWN"]
    del df["SUMUP"]
    del df["SUMDOWN"]

    return df
