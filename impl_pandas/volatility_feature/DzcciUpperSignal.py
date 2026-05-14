import pandas as pd

from impl_pandas.helpers import scale_01


def signal(df, n, factor_name, config):
    # DzcciUpperSignal indicator (Close - CCI Bollinger Upper band, 0-1 normalized)
    # Formula: CCI = (TP - MA(TP,N)) / (0.015 * MD(TP,N)) where TP=(H+L+C)/3
    #          CCI_UPPER = MA(CCI,N) + 2*STD(CCI,N); result = scale_01(CLOSE - CCI_UPPER, N, config.normalize_eps, config=config)
    # Measures how far the close price is above the CCI upper Bollinger band.
    # Positive signal values indicate close is breaking above the upper band (overbought or breakout signal).
    tp = df[["high", "low", "close"]].sum(axis=1) / 3.0
    ma = tp.rolling(n, min_periods=config.min_periods).mean()
    md = (tp - ma).abs().rolling(n, min_periods=config.min_periods).mean()
    cci = (tp - ma) / (config.normalize_eps + 0.015 * md)
    cci_middle = pd.Series(cci).rolling(n, min_periods=config.min_periods).mean()
    cci_upper = cci_middle + 2 * pd.Series(cci).rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)

    s = df["close"] - cci_upper
    df[factor_name] = scale_01(s, n, config.normalize_eps, config=config)

    return df
