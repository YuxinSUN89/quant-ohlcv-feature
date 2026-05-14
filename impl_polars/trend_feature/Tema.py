import polars as pl


def signal(df, n, factor_name, config):
    # Tema indicator
    eps = config.eps
    """
    N=20,40
    TEMA=3*EMA(CLOSE,N)-3*EMA(EMA(CLOSE,N),N)+EMA(EMA(EMA(CLOSE,N),N),N)
    TEMA combines single, double and triple EMAs, with less lag than ordinary moving averages.
    We use crossings of fast and slow TEMA to generate trading signals.
    """
    df = df.with_columns(pl.Series("ema", df["close"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("ema_ema", df["ema"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("ema_ema_ema", df["ema_ema"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    # TEMA=3*EMA(CLOSE,N)-3*EMA(EMA(CLOSE,N),N)+EMA(EMA(EMA(CLOSE,N),N),N)
    df = df.with_columns(pl.Series("TEMA", 3 * df["ema"] - 3 * df["ema_ema"] + df["ema_ema_ema"]))
    # normalize
    df = df.with_columns(pl.Series(factor_name, df["ema"] / (df["TEMA"] + eps) - 1))

    return df
