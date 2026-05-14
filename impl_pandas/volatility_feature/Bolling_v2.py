def signal(df, n, factor_name, config):
    # Bolling_v2 indicator (Bollinger bandwidth with ±0.5σ bands)
    # Formula: UPPER = MA + 0.5*STD; LOWER = MA - 0.5*STD
    #          result = (UPPER - LOWER) / MA = STD / MA
    # Computes the normalized width of ±0.5σ Bollinger bands (= STD/MA, i.e., coefficient of variation).
    # Higher values indicate greater relative price dispersion; lower values indicate price compression.
    eps = config.eps
    df["median"] = df["close"].rolling(n, min_periods=config.min_periods).mean()
    df["std"] = df["close"].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
    df["upper"] = df["median"] + 0.5 * df["std"]
    df["lower"] = df["median"] - 0.5 * df["std"]
    df[factor_name] = (df["upper"] - df["lower"]) / (df["median"] + eps)

    # delete extra columns
    del df["median"], df["std"], df["upper"], df["lower"]

    return df
