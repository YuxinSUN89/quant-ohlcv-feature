import pandas as pd

from impl_pandas.helpers import scale_zscore


def signal(df, n, factor_name, config):
    # DzcciLowerSignal indicator (CCI Bollinger Lower band - Close, z-score normalized)
    # Formula: CCI = (TP - MA(TP,N)) / (0.015 * MD(TP,N)) where TP=(H+L+C)/3
    #          CCI_LOWER = MA(CCI,N) - 2*STD(CCI,N); result = ZSCORE(CCI_LOWER - CLOSE, N)
    # Measures how far the CCI lower Bollinger band is below the current close, z-score normalized.
    # Positive values suggest close is above the CCI lower band; negative values suggest oversold conditions.
    tp = df[["high", "low", "close"]].sum(axis=1) / 3.0
    ma = tp.rolling(n, min_periods=config.min_periods).mean()
    md = (tp - ma).abs().rolling(n, min_periods=config.min_periods).mean()
    cci = (tp - ma) / (config.normalize_eps + 0.015 * md)
    cci_middle = pd.Series(cci).rolling(n, min_periods=config.min_periods).mean()
    cci_lower = cci_middle - 2 * pd.Series(cci).rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)

    s = cci_lower - df["close"]
    df[factor_name] = scale_zscore(s, n, config=config)

    return df
