import polars as pl


def signal(df, n, factor_name, config):
    # BollingWidth indicator (Adaptive Bollinger Width)
    # Formula: Z_SCORE = |CLOSE - MA| / STD; M = MA(Z_SCORE, N) (rolling mean of z-scores)
    #          UPPER = MA + STD*M; LOWER = MA - STD*M
    #          result = 2 * STD * M / MA (= bandwidth normalized by MA)
    # An adaptive version of Bollinger bandwidth where band width is determined by the rolling
    # mean of historical z-scores rather than a fixed multiplier. Wider bands indicate higher
    # recent volatility relative to the moving average.
    eps = config.eps
    df = df.with_columns(pl.Series("median", df["close"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("std", df["close"].rolling_std(n, ddof=config.ddof, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("z_score", (abs(df["close"] - df["median"]) / (df["std"] + config.eps)).fill_nan(None)))
    df = df.with_columns(pl.Series("m", df["z_score"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("upper", df["median"] + df["std"] * df["m"]))
    df = df.with_columns(pl.Series("lower", df["median"] - df["std"] * df["m"]))
    df = df.with_columns(pl.Series(factor_name, df["std"] * df["m"] * 2 / (df["median"] + eps)))

    # delete extra columns
    df = df.drop(["median", "std", "z_score", "m"])
    df = df.drop(["upper", "lower"])

    return df
