import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Ko indicator
    eps = config.eps
    # Ko indicator (Klinger Oscillator variant)
    # Formula: PRICE = (HIGH+LOW+CLOSE)/3; V = +VOLUME if PRICE > REF(PRICE,1) else -VOLUME
    #          KO = EMA(V, N) - EMA(V, N*1.618); normalized to [0, 1]
    # Ko classifies volume as positive (up-day) or negative (down-day) based on typical price direction,
    # then computes the difference between short and long EMAs of the signed volume.
    # Rising KO suggests accumulation (buying pressure); falling KO suggests distribution (selling pressure).
    df = df.with_columns(pl.Series("price", (df["high"] + df["low"] + df["close"]) / 3))
    df = df.with_columns(
        pl.Series("V", np.where(df["price"] > df["price"].shift(1), df["volume"], -df["volume"])).fill_nan(None)
    )
    df = df.with_columns(pl.Series("V_ema1", df["V"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("V_ema2", df["V"].ewm_mean(span=int(n * 1.618), adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("KO", df["V_ema1"] - df["V_ema2"]))
    # normalize
    df = df.with_columns(
        pl.Series(
            factor_name,
            (df["KO"] - df["KO"].rolling_min(n, min_samples=config.min_periods))
            / (
                df["KO"].rolling_max(n, min_samples=config.min_periods)
                - df["KO"].rolling_min(n, min_samples=config.min_periods)
                + eps
            ),
        )
    )

    # remove redundant columns
    df = df.drop(["price", "V", "V_ema1", "V_ema2", "KO"])

    return df
