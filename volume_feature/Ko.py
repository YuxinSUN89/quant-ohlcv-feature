import numpy as np


def signal(df, n, factor_name, config):
    # Ko indicator
    eps = config.eps
    # Ko indicator (Klinger Oscillator variant)
    # Formula: PRICE = (HIGH+LOW+CLOSE)/3; V = +VOLUME if PRICE > REF(PRICE,1) else -VOLUME
    #          KO = EMA(V, N) - EMA(V, N*1.618); normalized to [0, 1]
    # Ko classifies volume as positive (up-day) or negative (down-day) based on typical price direction,
    # then computes the difference between short and long EMAs of the signed volume.
    # Rising KO suggests accumulation (buying pressure); falling KO suggests distribution (selling pressure).
    df["price"] = (df["high"] + df["low"] + df["close"]) / 3
    df["V"] = np.where(df["price"] > df["price"].shift(1), df["volume"], -df["volume"])
    df["V_ema1"] = df["V"].ewm(span=n, adjust=config.ewm_adjust).mean()
    df["V_ema2"] = df["V"].ewm(span=int(n * 1.618), adjust=config.ewm_adjust).mean()
    df["KO"] = df["V_ema1"] - df["V_ema2"]
    # normalize
    df[factor_name] = (df["KO"] - df["KO"].rolling(n, min_periods=config.min_periods).min()) / (
        df["KO"].rolling(n, min_periods=config.min_periods).max()
        - df["KO"].rolling(n, min_periods=config.min_periods).min()
        + eps
    )

    # remove redundant columns
    del df["price"], df["V"], df["V_ema1"], df["V_ema2"], df["KO"]

    return df
