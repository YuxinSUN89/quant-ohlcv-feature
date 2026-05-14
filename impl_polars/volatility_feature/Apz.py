import polars as pl


def signal(df, n, factor_name, config):
    """
    N=10
    M=20
    PARAM=2
    VOL=EMA(EMA(HIGH-LOW,N),N)
    UPPER=EMA(EMA(CLOSE,M),M)+PARAM*VOL
    LOWER= EMA(EMA(CLOSE,M),M)-PARAM*VOL
    APZ (Adaptive Price Zone) is similar to Bollinger Bands and the Keltner Channel:
    all are price channels built around a moving average based on price volatility.
    The difference lies in how volatility is measured: Bollinger Bands use the standard
    deviation of the close, the Keltner Channel uses the true range ATR, and APZ uses
    the N-day double exponential average of the high-low difference to measure price amplitude.
    """
    df = df.with_columns(pl.Series("hl", df["high"] - df["low"]))
    df = df.with_columns(pl.Series("ema_hl", df["hl"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("vol", df["ema_hl"].ewm_mean(span=n, adjust=config.ewm_adjust)))

    # calculate the channel; can be used as a CTA strategy or adapted as a factor
    df = df.with_columns(pl.Series("ema_close", df["close"].ewm_mean(span=2 * n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("ema_ema_close", df["ema_close"].ewm_mean(span=2 * n, adjust=config.ewm_adjust)))
    # normalize using EMA
    df = df.with_columns(pl.Series(factor_name, df["vol"] / df["ema_ema_close"]))

    df = df.drop("hl")
    df = df.drop("ema_hl")
    df = df.drop("vol")
    df = df.drop("ema_close")
    df = df.drop("ema_ema_close")

    return df
