from impl_pandas.helpers import scale_01


def signal(df, n, factor_name, config):
    # Bias36 indicator (Bias36 minus its rolling MA, 0-1 normalized)
    # Formula: BIAS36 = MA(CLOSE,3) - MA(CLOSE,6); BIAS36_MA = MA(BIAS36, N)
    #          result = scale_01(BIAS36 - BIAS36_MA, N, config.normalize_eps, config=config)
    # Measures whether the short/medium MA spread (Bias36) is above or below its own average.
    # Normalized to [0,1] for comparability. High values indicate widening upward spread.
    bias36 = (
        df["close"].rolling(3, min_periods=config.min_periods).mean()
        - df["close"].rolling(6, min_periods=config.min_periods).mean()
    )
    bias36_ma = bias36.rolling(n, min_periods=config.min_periods).mean()

    s = bias36 - bias36_ma
    df[factor_name] = scale_01(s, n, config.normalize_eps, config=config)

    return df
