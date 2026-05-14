
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
    df["pmar"] = abs(df["close"] / (df["sma"] + config.eps))

    # percentile rank via numpy — count how many of the past N values the current value exceeds
    pmar_np = df["pmar"].to_numpy()
    result = np.full(len(pmar_np), np.nan)
    min_periods = config.min_periods or 1
    for i in range(min_periods - 1, len(pmar_np)):
        start = max(0, i - n)
        window = pmar_np[start : i + 1]
        result[i] = np.sum(window < pmar_np[i]) / n * 100
    df[factor_name] = result

    # remove redundant columns
    del df["sma"], df["pmar"]

    return df
