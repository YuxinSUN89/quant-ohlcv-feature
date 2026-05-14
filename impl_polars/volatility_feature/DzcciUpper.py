import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # DzcciUpper indicator (CCI Bollinger Upper band, 0-1 normalized)
    # Formula: CCI = (TP - MA(TP,N)) / (0.015 * MD(TP,N)) where TP=(H+L+C)/3
    #          CCI_UPPER = MA(CCI,N) + 2*STD(CCI,N); result = scale_01(CCI_UPPER, N, config.normalize_eps)
    # Captures the absolute level of the CCI upper Bollinger band, normalized to [0,1].
    # High values indicate CCI is in overbought territory with an elevated upper band.
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    ma = tp.rolling_mean(n, min_samples=config.min_periods)
    md = (tp - ma).abs().rolling_mean(n, min_samples=config.min_periods)
    cci = (tp - ma) / (config.normalize_eps + 0.015 * md)
    cci_middle = pl.Series(cci).rolling_mean(n, min_samples=config.min_periods)
    cci_upper = cci_middle + 2 * pl.Series(cci).rolling_std(n, min_samples=config.min_periods, ddof=config.ddof)

    s = cci_upper
    df = df.with_columns(pl.Series(factor_name, scale_01(s, n, config.normalize_eps, config=config)))

    return df
