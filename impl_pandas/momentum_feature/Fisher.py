import numpy as np


def signal(df, n, factor_name, config):
    # FISHER indicator
    """
    N=20
    PARAM=0.3
    PRICE=(HIGH+LOW)/2
    PRICE_CH=2*(PRICE-MIN(LOW,N)/(MAX(HIGH,N)-MIN(LOW,N))-0.5)
    PRICE_CHANGE=0.999 IF PRICE_CHANGE>0.99
    PRICE_CHANGE=-0.999 IF PRICE_CHANGE<-0.99
    PRICE_CHANGE=PARAM*PRICE_CH+(1-PARAM)*REF(PRICE_CHANGE,1)
    FISHER=0.5*REF(FISHER,1)+0.5*log((1+PRICE_CHANGE)/(1-PRICE_CHANGE))
    PRICE_CH measures the current price position between the highest and lowest prices over the past N periods.
    Fisher Transformation is a method that transforms stock price data to approximate a normal distribution.
    The advantage of the Fisher indicator is that it reduces the lag compared to common technical indicators.
    """
    PARAM = 1 / n
    df["price"] = (df["high"] + df["low"]) / 2
    df["min_low"] = df["low"].rolling(n, min_periods=config.min_periods).min()
    df["max_high"] = df["high"].rolling(n, min_periods=config.min_periods).max()
    df["price_ch"] = 2 * (df["price"] - df["min_low"]) / (df["max_high"] - df["min_low"] + config.eps) - 0.5
    df["price_change"] = PARAM * df["price_ch"] + (1 - PARAM) * df["price_ch"].shift(1)
    df["price_change"] = np.where(df["price_change"] > 0.99, 0.999, df["price_change"])
    df["price_change"] = np.where(df["price_change"] < -0.99, -0.999, df["price_change"])
    df[factor_name] = 0.5 * np.log((1 + df["price_change"]) / (1 - df["price_change"]))

    del df["price"]
    del df["min_low"]
    del df["max_high"]
    del df["price_ch"]
    del df["price_change"]

    return df
