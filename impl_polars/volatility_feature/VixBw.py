import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # VixBw indicator (VIX Bollinger width × trend direction)
    # Formula: VIX = CLOSE/REF(CLOSE,N)-1; VIX_UPPER/LOWER = adaptive Bollinger bands on VIX
    #          result = (VIX_UPPER - VIX_LOWER) * SIGN(diff(VIX_MA, N))
    #          zeroed when short-term trend direction conflicts with long-term trend direction
    # Measures the adaptive bandwidth of a VIX-like return measure, signed by its trend direction.
    # Positive values indicate widening volatility in an uptrend; negative in a downtrend.
    df = df.with_columns(pl.Series("vix", df["close"] / (df["close"].shift(n) + config.eps) - 1))
    df = df.with_columns(pl.Series("vix_median", df["vix"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(
        pl.Series("vix_std", df["vix"].rolling_std(n, min_samples=config.min_periods, ddof=config.ddof))
    )
    df = df.with_columns(pl.Series("vix_score", (abs(df["vix"] - df["vix_median"]) / df["vix_std"]).fill_nan(None)))
    df = df.with_columns(pl.Series("max", df["vix_score"].rolling_mean(n, min_samples=config.min_periods).shift(1)))
    df = df.with_columns(pl.Series("min", df["vix_score"].rolling_min(n, min_samples=config.min_periods).shift(1)))
    df = df.with_columns(pl.Series("vix_upper", df["vix_median"] + df["max"] * df["vix_std"]))
    df = df.with_columns(pl.Series("vix_lower", df["vix_median"] - df["max"] * df["vix_std"]))
    # Use .to_numpy() explicitly so np.sign returns a numpy array (not polars Series),
    # which preserves NaN != NaN = True semantics matching pandas behaviour.
    _sign_n = np.sign(df["vix_median"].diff(n).to_numpy())
    _sign_1 = np.sign(df["vix_median"].diff(1).to_numpy())
    _sign_1s = np.sign(df["vix_median"].diff(1).shift(1).to_numpy())
    df = df.with_columns(pl.Series(factor_name, (df["vix_upper"] - df["vix_lower"]) * _sign_n))
    condition1 = _sign_n != _sign_1
    condition2 = _sign_n != _sign_1s
    df = df.with_columns(pl.when(pl.Series(condition1)).then(0.0).otherwise(pl.col(factor_name)).alias(factor_name))
    df = df.with_columns(pl.when(pl.Series(condition2)).then(0.0).otherwise(pl.col(factor_name)).alias(factor_name))
    # normalize using ATR indicator

    df = df.drop("vix")
    df = df.drop("vix_median")
    df = df.drop("vix_std")
    df = df.drop("max")
    df = df.drop("min")
    df = df.drop(["vix_upper", "vix_lower"])

    return df
