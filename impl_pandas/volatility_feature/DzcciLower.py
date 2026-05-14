import pandas as pd


def signal(df, n, factor_name, config):
    # DzcciLower indicator (CCI Bollinger Lower band - CCI short MA)
    # Formula: CCI = (TP - MA(TP,N)) / (0.015 * MD(TP,N)) where TP=(H+L+C)/3
    #          CCI_LOWER = MA(CCI,N) - 2*STD(CCI,N); CCI_MA = MA(CCI, N/4)
    #          result = CCI_LOWER - CCI_MA
    # Applies Bollinger Band logic to CCI, then measures how far the lower CCI band is
    # below the short-term CCI MA. Negative values suggest CCI is compressed above its lower band.
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    _ma = tp.rolling(n, min_periods=config.min_periods).mean()
    md = (tp - _ma).abs().rolling(n, min_periods=config.min_periods).mean()
    _cci = (tp - _ma) / (config.normalize_eps + 0.015 * md)
    cci_middle = pd.Series(_cci).rolling(n, min_periods=config.min_periods).mean()
    cci_lower = cci_middle - 2 * pd.Series(_cci).rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
    cci_ma = pd.Series(_cci).rolling(max(1, int(n / 4)), min_periods=config.min_periods).mean()

    s = cci_lower - cci_ma
    df[factor_name] = pd.Series(s)

    return df
