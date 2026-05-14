import numpy as np


def signal(df, n, factor_name, config):
    # VixBw indicator (VIX Bollinger width × trend direction)
    # Formula: VIX = CLOSE/REF(CLOSE,N)-1; VIX_UPPER/LOWER = adaptive Bollinger bands on VIX
    #          result = (VIX_UPPER - VIX_LOWER) * SIGN(diff(VIX_MA, N))
    #          zeroed when short-term trend direction conflicts with long-term trend direction
    # Measures the adaptive bandwidth of a VIX-like return measure, signed by its trend direction.
    # Positive values indicate widening volatility in an uptrend; negative in a downtrend.
    df["vix"] = df["close"] / df["close"].shift(n) - 1
    df["vix_median"] = df["vix"].rolling(window=n, min_periods=config.min_periods).mean()
    df["vix_std"] = df["vix"].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
    df["vix_score"] = abs(df["vix"] - df["vix_median"]) / df["vix_std"]
    df["max"] = df["vix_score"].rolling(window=n, min_periods=config.min_periods).mean().shift(1)
    df["min"] = df["vix_score"].rolling(window=n, min_periods=config.min_periods).min().shift(1)
    df["vix_upper"] = df["vix_median"] + df["max"] * df["vix_std"]
    df["vix_lower"] = df["vix_median"] - df["max"] * df["vix_std"]
    df[factor_name] = (df["vix_upper"] - df["vix_lower"]) * np.sign(df["vix_median"].diff(n))
    condition1 = np.sign(df["vix_median"].diff(n)) != np.sign(df["vix_median"].diff(1))
    condition2 = np.sign(df["vix_median"].diff(n)) != np.sign(df["vix_median"].diff(1).shift(1))
    df.loc[condition1, factor_name] = 0
    df.loc[condition2, factor_name] = 0
    # normalize using ATR indicator

    del df["vix"]
    del df["vix_median"]
    del df["vix_std"]
    del df["max"]
    del df["min"]
    del df["vix_upper"], df["vix_lower"]

    return df
