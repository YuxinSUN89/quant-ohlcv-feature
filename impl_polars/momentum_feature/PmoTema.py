import polars as pl


def signal(df, n, factor_name, config):
    # PmoTema indicator (PMO using TEMA instead of CLOSE)
    # Formula: TEMA = 3*EMA - 3*EMA(EMA) + EMA(EMA(EMA))
    #          ROC = (TEMA - REF(TEMA,1)) / REF(TEMA,1) * 100
    #          PMO_TEMA = MA(MA(ROC,N)*10, 4N) smoothed by MA(2N)
    # A Price Momentum Oscillator computed on the Triple EMA (TEMA) instead of close price.
    # TEMA reduces lag; the double smoothing of ROC produces a slow, signal-line-like oscillator.
    # TEMA moving average
    df = df.with_columns(pl.Series("ema", df["close"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("ema_ema", df["ema"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("ema_ema_ema", df["ema_ema"].ewm_mean(span=n, adjust=config.ewm_adjust)))
    df = df.with_columns(pl.Series("TEMA", 3 * df["ema"] - 3 * df["ema_ema"] + df["ema_ema_ema"]))

    # calculate PMO
    df = df.with_columns(
        pl.Series("ROC", (df["TEMA"] - df["TEMA"].shift(1)) / df["TEMA"].shift(1) * 100)
    )  # use TEMA moving average instead of original CLOSE
    df = df.with_columns(
        pl.Series("ROC_MA", df["ROC"].rolling_mean(n, min_samples=config.min_periods))
    )  # use moving average instead of dynamic moving average
    df = df.with_columns(pl.Series("ROC_MA10", df["ROC_MA"] * 10))
    df = df.with_columns(pl.Series("PMO", df["ROC_MA10"].rolling_mean(4 * n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series(factor_name, df["PMO"].rolling_mean(2 * n, min_samples=config.min_periods)))

    df = df.drop(["ema", "ema_ema", "ema_ema_ema", "TEMA"])
    df = df.drop(["ROC", "ROC_MA"])
    df = df.drop("ROC_MA10")
    df = df.drop("PMO")

    return df
