import polars as pl


def signal(df, n, factor_name, config):
    # DzcciLower indicator (CCI Bollinger Lower band - CCI short MA)
    # Formula: CCI = (TP - MA(TP,N)) / (0.015 * MD(TP,N)) where TP=(H+L+C)/3
    #          CCI_LOWER = MA(CCI,N) - 2*STD(CCI,N); CCI_MA = MA(CCI, N/4)
    #          result = CCI_LOWER - CCI_MA
    # Applies Bollinger Band logic to CCI, then measures how far the lower CCI band is
    # below the short-term CCI MA. Negative values suggest CCI is compressed above its lower band.
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    _ma = tp.rolling_mean(n, min_samples=config.min_periods)
    md = (tp - _ma).abs().rolling_mean(n, min_samples=config.min_periods)
    _cci = (tp - _ma) / (config.normalize_eps + 0.015 * md)
    cci_middle = pl.Series(_cci).rolling_mean(n, min_samples=config.min_periods)
    cci_lower = cci_middle - 2 * pl.Series(_cci).rolling_std(n, min_samples=config.min_periods, ddof=config.ddof)
    cci_ma = pl.Series(_cci).rolling_mean(max(1, int(n / 4)), min_samples=config.min_periods)

    s = cci_lower - cci_ma
    df = df.with_columns(pl.Series(factor_name, s))

    return df
