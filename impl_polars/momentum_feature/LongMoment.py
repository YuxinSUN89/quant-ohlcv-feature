import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # LongMoment indicator (Momentum based on low-amplitude candles)
    # Formula: PRICE_CHANGE = CLOSE.pct_change(N); AMPLITUDE = HIGH/LOW - 1
    #          Within a 10N rolling window, select the 70% lowest-amplitude candles,
    #          result = SUM of their PRICE_CHANGEs
    # Captures momentum signal from low-amplitude (quiet) candles, filtering out noisy high-volatility bars.
    # Positive values indicate sustained upward moves during calm periods (stronger signal quality).
    def range_plus(x, np_tmp, rolling_window, lam):
        # calculate the rolling index
        li = x.index.to_list()
        # extract the corresponding index block from the full array
        np_tmp2 = np_tmp[li, :]
        # sort by amplitude
        np_tmp2 = np_tmp2[np.argsort(np_tmp2[:, 0])]
        # calculate the number of splits needed
        t = int(rolling_window * lam)
        # calculate low-price return factor
        np_tmp2 = np_tmp2[:t, :]
        s = np_tmp2[:, 1].sum()
        return s

    df = df.with_columns(pl.Series("price_change", df["close"].pct_change(n)))
    # calculate cut momentum and reversal factor for window 20-180
    df = df.with_columns(pl.Series("amplitude", (df["high"] / df["low"]) - 1))
    # convert columns to numpy arrays for rolling window computation
    np_amp = np.array(df["amplitude"], dtype=float)
    np_pc = np.array(df["price_change"], dtype=float)
    # calculate the factor using rolling window
    window = n * 10
    result = np.full(len(df), np.nan)
    for i in range(window - 1, len(df)):
        block = np.column_stack([np_amp[i - window + 1 : i + 1], np_pc[i - window + 1 : i + 1]])
        block = block[np.argsort(block[:, 0])]
        t = int(window * 0.7)
        result[i] = block[:t, 1].sum()
    df = df.with_columns(pl.Series(factor_name, result))

    df = df.drop(["amplitude", "price_change"])

    return df
