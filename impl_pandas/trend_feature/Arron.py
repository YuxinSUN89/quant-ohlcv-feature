import numba as nb
import numpy as np
import pandas as pd

from impl_pandas.helpers import scale_zscore


# ===== Function: zscore normalization
@nb.njit(nb.int32[:](nb.float64[:], nb.int32), cache=True)
def rolling_argmin_queue(arr, n):
    results = np.empty(len(arr), dtype=np.int32)

    head = 0
    tail = 0
    que_idx = np.empty(len(arr), dtype=np.int32)
    for i, x in enumerate(arr[:n]):
        while tail > 0 and arr[que_idx[tail - 1]] > x:
            tail -= 1
        que_idx[tail] = i
        tail += 1
        results[i] = que_idx[0]

    for i, x in enumerate(arr[n:], n):
        if que_idx[head] <= i - n:
            head += 1
        while tail > head and arr[que_idx[tail - 1]] > x:
            tail -= 1
        que_idx[tail] = i
        tail += 1
        results[i] = que_idx[head]
    return results


def signal(df, n, factor_name, config):
    # ******************** Arron ********************
    # ArronUp = (N - HIGH_LEN) / N * 100
    # ArronDown = (N - LOW_LEN) / N * 100
    # ArronOs = ArronUp - ArronDown
    # where HIGH_LEN, LOW_LEN are the number of days since the highest/lowest price in the past N days
    # ArronUp and ArronDown represent the distance from the current time to when the high/low occurred,
    # as a percentage of the period length.
    # If the price makes a new high today, ArronUp equals 100; a new low, ArronDown equals 100.
    # The Aroon indicator is the difference between the two, ranging from -100 to 100.
    # Aroon > 0 indicates an uptrend; Aroon < 0 indicates a downtrend.
    # The farther from 0, the stronger the trend. Here we use 20/-20 as thresholds.
    # A buy/sell signal is generated when ArronOs crosses above 20 / below -20.
    low_len = rolling_argmin_queue(np.array(df["low"].values, dtype=np.float64), np.int32(n))
    high_len = rolling_argmin_queue(np.array(-df["high"].values, dtype=np.float64), np.int32(n))

    s = pd.Series((high_len - low_len) * 100 / n)
    df[factor_name] = scale_zscore(s, n, config=config)

    return df
