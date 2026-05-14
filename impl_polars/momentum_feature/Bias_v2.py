import polars as pl
import talib as ta


def signal(df, n, factor_name, config):
    # Bias_v2 indicator (Volume-weighted bias on regression-smoothed close)
    # Formula: CLOSE_REG = EMA(LINEARREG(CLOSE,N), N); MA = MA(CLOSE_REG, N)
    #          CLOSE_HL = (HIGH + LOW)/2 * VOLUME; result = CLOSE_HL / MA - 1
    # Uses linear regression followed by EMA to smooth the close, then computes bias of
    # volume-weighted midpoint price relative to the smoothed MA.
    eps = config.eps
    # calculate linear regression
    df = df.with_columns(pl.Series("new_close", ta.LINEARREG(df["close"], timeperiod=n)))
    # smooth the curve again with EMA
    df = df.with_columns(pl.Series("new_close", ta.EMA(df["new_close"], timeperiod=n)))
    # calculate middle band using the new close price
    # fill_nan(None) converts float NaN (from talib NaN head) to polars null so rolling_mean skips them
    ma = df["new_close"].fill_nan(None).rolling_mean(n, min_samples=config.min_periods)
    # redefine close as (high + low) / 2 * volume
    # df['close'] =   (df['high'] + df['low']) / 2 * df['volume']
    close = (df["high"] + df["low"]) / 2 * df["volume"]
    # calculate bias
    df = df.with_columns(pl.Series(factor_name, close / (ma + eps) - 1))

    df = df.drop("new_close")

    return df
