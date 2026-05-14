"""Common helper functions shared across polars indicator files."""

import numpy as np
import polars as pl


def scale_01(_s, _n, eps, config):
    """Min-max normalisation to [0, 1].

    ``(value - rolling_min) / (eps + rolling_max - rolling_min)``
    """
    _s = (pl.Series(_s) - pl.Series(_s).rolling_min(_n, min_samples=config.min_periods)) / (
        eps
        + pl.Series(_s).rolling_max(_n, min_samples=config.min_periods)
        - pl.Series(_s).rolling_min(_n, min_samples=config.min_periods)
    )
    return pl.Series(_s)


def scale_zscore(_s, _n, config):
    """Z-score normalisation: ``(value - rolling_mean) / rolling_std``."""
    _s = (pl.Series(_s) - pl.Series(_s).rolling_mean(_n, min_samples=config.min_periods)) / pl.Series(_s).rolling_std(
        _n, min_samples=config.min_periods, ddof=config.ddof
    )
    return pl.Series(_s)


def rolling_corr_np(s1, s2, n, min_periods, config):
    """Rolling Pearson correlation via numpy.

    NaN pairs are dropped from each window; at least *min_periods* valid pairs required.
    """
    a1 = s1.to_numpy()
    a2 = s2.to_numpy()
    result = np.full(len(a1), np.nan)
    for i in range(len(a1)):
        start = max(0, i - n + 1)
        w1 = a1[start : i + 1]
        w2 = a2[start : i + 1]
        valid = ~(np.isnan(w1) | np.isnan(w2))
        w1v, w2v = w1[valid], w2[valid]
        if len(w1v) < min_periods:
            continue
        if np.std(w1v) == 0 or np.std(w2v) == 0:
            result[i] = np.nan
            continue
        result[i] = np.corrcoef(w1v, w2v)[0, 1]
    return pl.Series(result)


def sma_recursive(ser, n, m):
    """Recursive SMA: ``SMA(X,N,M) = M/N*X + (N-M)/N*ref(SMA,1)``."""
    ser = ser.fill_null(0)
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

    :param df: polars DataFrame
    :param param_list: list of period values
    :param column: column name to average
    :param config: IndicatorConfig
    """
    ret = dict()
    for param in param_list:
        n = int(param)
        ret[str(param)] = df[column].rolling_mean(n, min_samples=config.min_periods)
    return ret
