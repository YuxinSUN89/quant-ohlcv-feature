import numpy as np


def signal(df, n, factor_name, config):
    # LongMoment indicator (Momentum based on low-amplitude candles)
    # Formula: PRICE_CHANGE = CLOSE.pct_change(N); AMPLITUDE = HIGH/LOW - 1
    #          Within a 10N rolling window, select the 70% lowest-amplitude candles,
    #          result = SUM of their PRICE_CHANGEs
    # Captures momentum signal from low-amplitude (quiet) candles, filtering out noisy high-volatility bars.
    # Positive values indicate sustained upward moves during calm periods (stronger signal quality).
    # convert columns to numpy arrays for rolling window computation
    price_change = df["close"].pct_change(n)
    amplitude = (df["high"] / df["low"]) - 1
    np_amp = np.array(amplitude, dtype=float)
    np_pc = np.array(price_change, dtype=float)
    # calculate the factor using rolling window
    window = n * 10
    result = np.full(len(df), np.nan)
    for i in range(window - 1, len(df)):
        block = np.column_stack([np_amp[i - window + 1 : i + 1], np_pc[i - window + 1 : i + 1]])
        block = block[np.argsort(block[:, 0])]
        t = int(window * 0.7)
        result[i] = block[:t, 1].sum()
    df[factor_name] = result

    return df
