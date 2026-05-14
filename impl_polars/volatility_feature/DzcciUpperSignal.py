import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # DzcciUpperSignal indicator (Close - CCI Bollinger Upper band, 0-1 normalized)
    # Formula: CCI = (TP - MA(TP,N)) / (0.015 * MD(TP,N)) where TP=(H+L+C)/3
    #          CCI_UPPER = MA(CCI,N) + 2*STD(CCI,N); result = scale_01(CLOSE - CCI_UPPER, N, config.normalize_eps)
    # Measures how far the close price is above the CCI upper Bollinger band.
    # Positive signal values indicate close is breaking above the upper band (overbought or breakout signal).
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    ma = tp.rolling_mean(n, min_samples=config.min_periods)
    md = (tp - ma).abs().rolling_mean(n, min_samples=config.min_periods)
    cci = (tp - ma) / (config.normalize_eps + 0.015 * md)
    cci_middle = pl.Series(cci).rolling_mean(n, min_samples=config.min_periods)
    cci_upper = cci_middle + 2 * pl.Series(cci).rolling_std(n, min_samples=config.min_periods, ddof=config.ddof)

    s = df["close"] - cci_upper
    df = df.with_columns(pl.Series(factor_name, scale_01(s, n, config.normalize_eps, config=config)))

    return df
