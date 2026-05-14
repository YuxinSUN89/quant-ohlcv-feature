import numpy as np
import polars as pl


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
    df = df.with_columns(pl.Series("c1", abs(df["high"] - df["low"])))
    df = df.with_columns(pl.Series("c2", abs(df["close"] - df["close"].shift(1))))
    df = df.with_columns(pl.Series("c3", abs(df["high"] - df["close"].shift(1))))
    df = df.with_columns(TR=pl.max_horizontal([pl.col("c1"), pl.col("c2"), pl.col("c3")]))
    df = df.with_columns(pl.Series("ATR", df["TR"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series(factor_name, (df["high"] - df["low"].shift(1)) / (df["ATR"] * np.sqrt(n))))
    # df['RwiL'] = (df['high'].shift(1) - df['low']) / (df['ATR'] * np.sqrt(n))
    # df['Rwi'] = (df['close'] - df['RwiL']) / (config.normalize_eps + df['RwiH'] - df['RwiL'])
    # df[f'RwiH_bh_{n}'] = df['RwiH'].shift(1)
    # df[f'RwiL_bh_{n}'] = df['RwiL'].shift(1)
    # df[f'Rwi_bh_{n}'] = df['Rwi'].shift(1)

    df = df.drop("c1")
    df = df.drop("c2")
    df = df.drop("c3")
    df = df.drop("TR")
    df = df.drop("ATR")

    return df
