import numpy as np


def signal(df, n, factor_name, config):
    # Rwi indicator
    """
    N=14
    TR=MAX(ABS(HIGH-LOW),ABS(HIGH-REF(CLOSE,1)),ABS(REF(
    CLOSE,1)-LOW))
    ATR=MA(TR,N)
    RwiH=(HIGH-REF(LOW,1))/(ATR*sqrt(N))
    RwiL=(REF(HIGH,1)-LOW)/(ATR*sqrt(N))
    Rwi (Random Walk Index) compares the random walk range with the actual price range
    over a period of time to determine the price trend.
    If RwiH > 1, prices are in a long-term uptrend, generating a buy signal;
    if RwiL > 1, prices are in a long-term downtrend, generating a sell signal.
    """
    df["c1"] = abs(df["high"] - df["low"])
    df["c2"] = abs(df["close"] - df["close"].shift(1))
    df["c3"] = abs(df["high"] - df["close"].shift(1))
    df["TR"] = df[["c1", "c2", "c3"]].max(axis=1)
    df["ATR"] = df["TR"].rolling(n, min_periods=config.min_periods).mean()
    df[factor_name] = (df["high"] - df["low"].shift(1)) / (df["ATR"] * np.sqrt(n))
    # df['RwiL'] = (df['high'].shift(1) - df['low']) / (df['ATR'] * np.sqrt(n))
    # df['Rwi'] = (df['close'] - df['RwiL']) / (1e-9 + df['RwiH'] - df['RwiL'])
    # df[f'RwiH_bh_{n}'] = df['RwiH'].shift(1)
    # df[f'RwiL_bh_{n}'] = df['RwiL'].shift(1)
    # df[f'Rwi_bh_{n}'] = df['Rwi'].shift(1)

    del df["c1"]
    del df["c2"]
    del df["c3"]
    del df["TR"]
    del df["ATR"]

    return df
