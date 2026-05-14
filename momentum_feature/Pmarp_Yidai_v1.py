import numpy as np


# Factor indicator name version: Pmarp_Yidai_v1
def signal(df, n, factor_name, config):
    # Pmarp_Yidai_v1 indicator (Percentile rank of close vs MA ratio)
    # Formula: PMAR = |CLOSE / MA(CLOSE, N)|
    #          result = (number of past N candles with PMAR < current PMAR) / N * 100
    # Computes the rolling percentile rank of the absolute close-to-MA ratio over N periods.
    # High values indicate current price deviation from MA is unusually large (potential reversal point).

    # calculate sma
    df["sma"] = df["close"].rolling(n, min_periods=config.min_periods).mean()

    # compare current price to sma (percentage): relative price change vs moving average
    df["pmar"] = abs(df["close"] / df["sma"])

    # calculate how many candles in the statistical range the current candle's feature value exceeds? returns percentage
    # count how many candles' pmar the current candle's pmar exceeds within the statistical period
    df["pmarpSum"] = 0

    k = n
    while k > 0:
        df["pmardiff"] = df["pmar"] - df["pmar"].shift(k)
        df["add"] = np.where(df["pmardiff"] > 0, 1, 0)
        df["pmarpSum"] = df["pmarpSum"] + df["add"]
        k -= 1

    df[factor_name] = df["pmarpSum"] / n * 100

    # remove redundant columns
    del df["sma"], df["pmar"], df["pmardiff"], df["add"], df["pmarpSum"]

    return df
