import polars as pl


def signal(df, n, factor_name, config):
    # Cs_mtm_v2 indicator (Composite: price momentum × std momentum × volume momentum)
    # Formula: C_MTM = MA(CLOSE/REF(CLOSE,N)-1, N); S_MTM = MA(STD/REF(STD,N), N)
    #          V_MTM = MA(QUOTE_VOLUME/REF(QUOTE_VOLUME,N), N)
    #          result = C_MTM * S_MTM * V_MTM
    # Combines three rolling momentum signals: price, volatility, and volume.
    # High positive values indicate simultaneous upward trending in price, expanding volatility, and increasing volume.
    # close price momentum
    df = df.with_columns(pl.Series("c_mtm", df["close"] / (df["close"].shift(n) + config.eps) - 1))
    df = df.with_columns(pl.Series("c_mtm", df["c_mtm"].rolling_mean(n, min_samples=config.min_periods)))
    # standard deviation momentum
    df = df.with_columns(pl.Series("std", df["close"].rolling_std(n, ddof=config.ddof, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("s_mtm", df["std"] / (df["std"] + config.eps).shift(n)))
    df = df.with_columns(pl.Series("s_mtm", df["s_mtm"].rolling_mean(n, min_samples=config.min_periods)))
    # volume change
    df = df.with_columns(pl.Series("v_mtm", df["quote_volume"] / (df["quote_volume"].shift(n) + config.eps)))
    df = df.with_columns(pl.Series("v_mtm", df["v_mtm"].rolling_mean(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series(factor_name, df["c_mtm"] * df["s_mtm"] * df["v_mtm"]))

    df = df.drop(["c_mtm", "std", "s_mtm", "v_mtm"])

    return df
