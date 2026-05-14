import numpy as np


def signal(df, n, factor_name, config):
    # ShortMoment indicator (Momentum based on low-amplitude candles, short window)
    # Formula: PRICE_CHANGE = CLOSE.pct_change(N); AMPLITUDE = HIGH/LOW - 1
    #          Within an N rolling window, select the 70% lowest-amplitude candles,
    #          result = SUM of their PRICE_CHANGEs
    # A shorter-window version of LongMoment. Captures momentum from calm, low-volatility candles
    # within a tighter N-period window for quicker signal response.
    # convert columns to numpy arrays for rolling window computation
    price_change = df["close"].pct_change(n)
    amplitude = (df["high"] / df["low"]) - 1
    np_amp = np.array(amplitude, dtype=float)
    np_pc = np.array(price_change, dtype=float)
    # calculate the factor using rolling window
    window = n
    result = np.full(len(df), np.nan)
    for i in range(window - 1, len(df)):
        block = np.column_stack([np_amp[i - window + 1 : i + 1], np_pc[i - window + 1 : i + 1]])
        block = block[np.argsort(block[:, 0])]
        t = int(window * 0.7)
        result[i] = block[:t, 1].sum()
    df[factor_name] = result

    return df
