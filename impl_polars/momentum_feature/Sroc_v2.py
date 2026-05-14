import polars as pl
import talib as ta


def signal(df, n, factor_name, config):
    # Sroc_v2 indicator (KAMA-based Smoothed Rate of Change)
    # Formula: KAMA = KAMA(CLOSE, N); result = (KAMA - REF(KAMA, 2N)) / REF(KAMA, 2N)
    # Computes the rate of change of the Kaufman Adaptive Moving Average (KAMA) over 2N periods.
    # KAMA adapts to volatility, so SROC_v2 gives a momentum signal that is less sensitive to noise.
    eps = config.eps
    ema = ta.KAMA(df["close"], n)
    ref = ema.shift(2 * n)
    df = df.with_columns(pl.Series(factor_name, (ema - ref) / (ref + eps)))

    return df
