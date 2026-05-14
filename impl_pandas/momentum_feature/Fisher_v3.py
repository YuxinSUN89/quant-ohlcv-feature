import numpy as np


# FISHER_v3
def signal(df, n, factor_name, config):
    # FISHER_v3 indicator
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
    PARAM = 0.33  # 0.33
    df["price"] = (df["high"] + df["low"]) / 2
    df["min_low"] = df["low"].rolling(n, min_periods=config.min_periods).min()
    df["max_high"] = df["high"].rolling(n, min_periods=config.min_periods).max()
    df["price_ch"] = PARAM * 2 * ((df["price"] - df["min_low"]) / (df["max_high"] - df["min_low"]) - 0.5)
    df["price_change"] = df["price_ch"] + (1 - PARAM) * df["price_ch"].shift(1)
    df["price_change"] = np.where(df["price_change"] > 0.99, 0.999, df["price_change"])
    df["price_change"] = np.where(df["price_change"] < -0.99, -0.999, df["price_change"])

    df["price_change"] = 0.3 * df["price_change"] + 0.7 * df["price_change"].shift(1)
    df[factor_name] = 0.5 * df["price_change"].shift(1) + 0.5 * np.log(
        ((1 + df["price_change"]) / (1 - df["price_change"]))
    )

    # price = (df['high'] + df['low']) / 2.
    # low_min = df['low'].rolling(n, min_periods=config.min_periods).min()
    # high_max = df['high'].rolling(n, min_periods=config.min_periods).max()
    # price_ch = 2 * (price - 0.5 - low_min / (high_max - low_min))
    # price_ch = np.where(price_ch > 0.99, 0.99, price_ch)
    # price_ch = np.where(price_ch < -0.99, -0.99, price_ch)
    # price_ch = 0.3 * pd.Series(price_ch) + 0.7 * pd.Series(price_ch).shift(1)
    # fisher = 0.5 * pd.Series(price_ch).shift(1) + 0.5 * pd.Series(np.log((1 + price_ch) / (1 - price_ch)))
    #
    # signal = fisher
    # df[factor_name] = scale_01(signal, n, config.normalize_eps, config=config)

    return df
