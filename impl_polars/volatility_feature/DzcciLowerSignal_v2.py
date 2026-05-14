import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # DzcciLowerSignal_v2 indicator (CCI Bollinger Lower band - CCI short MA, 0-1 normalized)
    # Formula: CCI = (TP - MA(TP,N)) / (0.015 * MD(TP,N)) where TP=(H+L+C)/3
    #          CCI_LOWER = MA(CCI,N) - 2*STD(CCI,N); CCI_MA = MA(CCI, N/4)
    #          result = scale_01(CCI_LOWER - CCI_MA, N, config.normalize_eps)
    # Measures how far the CCI lower band is below the short-term CCI MA, normalized to [0,1].
    # Low values indicate CCI is compressed near or above its lower band; high values suggest expansion downward.
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    ma = tp.rolling_mean(n, min_samples=config.min_periods)
    md = (tp - ma).abs().rolling_mean(n, min_samples=config.min_periods)
    cci = (tp - ma) / (config.normalize_eps + 0.015 * md)
    cci_middle = pl.Series(cci).rolling_mean(n, min_samples=config.min_periods)
    cci_lower = cci_middle - 2 * pl.Series(cci).rolling_std(n, min_samples=config.min_periods, ddof=config.ddof)
    cci_ma = pl.Series(cci).rolling_mean(max(1, int(n / 4)), min_samples=config.min_periods)

    s = cci_lower - cci_ma
    df = df.with_columns(pl.Series(factor_name, scale_01(s, n, config.normalize_eps, config=config)))

    return df
