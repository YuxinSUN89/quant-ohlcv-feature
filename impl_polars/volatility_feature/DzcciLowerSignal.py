import polars as pl

from impl_polars.helpers import scale_zscore


def signal(df, n, factor_name, config):
    # DzcciLowerSignal indicator (CCI Bollinger Lower band - Close, z-score normalized)
    # Formula: CCI = (TP - MA(TP,N)) / (0.015 * MD(TP,N)) where TP=(H+L+C)/3
    #          CCI_LOWER = MA(CCI,N) - 2*STD(CCI,N); result = ZSCORE(CCI_LOWER - CLOSE, N)
    # Measures how far the CCI lower Bollinger band is below the current close, z-score normalized.
    # Positive values suggest close is above the CCI lower band; negative values suggest oversold conditions.
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    ma = tp.rolling_mean(n, min_samples=config.min_periods)
    md = (tp - ma).abs().rolling_mean(n, min_samples=config.min_periods)
    cci = (tp - ma) / (config.normalize_eps + 0.015 * md)
    cci_middle = pl.Series(cci).rolling_mean(n, min_samples=config.min_periods)
    cci_lower = cci_middle - 2 * pl.Series(cci).rolling_std(n, min_samples=config.min_periods, ddof=config.ddof)

    s = cci_lower - df["close"]
    df = df.with_columns(pl.Series(factor_name, scale_zscore(s, n, config=config)))

    return df
