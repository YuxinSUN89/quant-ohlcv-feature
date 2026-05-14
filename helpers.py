"""Common helper functions shared across pandas indicator files."""

import pandas as pd


def scale_01(_s, _n, eps, config):
    """Min-max normalisation to [0, 1].

    ``(value - rolling_min) / (eps + rolling_max - rolling_min)``
    """
    _s = (pd.Series(_s) - pd.Series(_s).rolling(_n, min_periods=config.min_periods).min()) / (
        eps
        + pd.Series(_s).rolling(_n, min_periods=config.min_periods).max()
        - pd.Series(_s).rolling(_n, min_periods=config.min_periods).min()
    )
    return _s


def scale_zscore(_s, _n, config):
    """Z-score normalisation: ``(value - rolling_mean) / rolling_std``."""
    _s = (pd.Series(_s) - pd.Series(_s).rolling(_n, min_periods=config.min_periods).mean()) / pd.Series(_s).rolling(
        _n, min_periods=config.min_periods
    ).std(ddof=config.ddof)
    return _s


def sma_recursive(ser, n, m):
    """Recursive SMA: ``SMA(X,N,M) = M/N*X + (N-M)/N*ref(SMA,1)``."""
    ser.fillna(value=0, inplace=True)
    _l = []
    for i, v in enumerate(ser):
        if i == 0:
            _l.append(v)
        else:
            r = m / n
            _l.append(r * v + (1 - r) * _l[-1])
    return _l


def rolling_mean_multi(df, param_list, column, config) -> dict:
    """Multi-period rolling mean for the same factor, ~3x faster than calling signal() repeatedly.

    :param df: DataFrame of k-line data
    :param param_list: list of period values
    :param column: column name to average
    :param config: IndicatorConfig
    """
    ret = dict()
    for param in param_list:
        n = int(param)
        ret[str(param)] = df[column].rolling(n, min_periods=config.min_periods).mean()
    return ret
