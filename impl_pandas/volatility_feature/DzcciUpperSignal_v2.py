import pandas as pd

from impl_pandas.helpers import scale_01


def signal(df, n, factor_name, config):
    # DzcciUpperSignal_v2 indicator (CCI short MA - CCI Bollinger Upper band, 0-1 normalized)
    # Formula: CCI = (TP - MA(TP,N)) / (0.015 * MD(TP,N)) where TP=(H+L+C)/3
    #          CCI_UPPER = MA(CCI,N) + 2*STD(CCI,N); CCI_MA = MA(CCI, N/4)
    #          result = scale_01(CCI_MA - CCI_UPPER, N, config.normalize_eps, config=config)
    # Measures how far the short-term CCI MA is below the upper Bollinger band on CCI.
    # Low values indicate CCI is pressing against or above the upper band (overbought signal).
    tp = df[["high", "low", "close"]].sum(axis=1) / 3.0
    ma = tp.rolling(n, min_periods=config.min_periods).mean()
    md = (tp - ma).abs().rolling(n, min_periods=config.min_periods).mean()
    cci = (tp - ma) / (config.normalize_eps + 0.015 * md)
    cci_middle = pd.Series(cci).rolling(n, min_periods=config.min_periods).mean()
    cci_upper = cci_middle + 2 * pd.Series(cci).rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
    cci_ma = pd.Series(cci).rolling(max(1, int(n / 4)), min_periods=config.min_periods).mean()

    s = cci_ma - cci_upper
    df[factor_name] = scale_01(s, n, config.normalize_eps, config=config)

    return df
