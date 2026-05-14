def signal(df, n, factor_name, config):
    eps = config.eps
    # Cvr_v0 indicator (Calmar-Volume Ratio)
    # Formula: CVR = (SUM(PCT_CHANGE, N) / STD(PCT_CHANGE, N)) * (QUOTE_VOLUME / MA(QUOTE_VOLUME, N))
    #          result = MA(CVR, N)
    # Combines a risk-adjusted return measure (cumulative return / volatility, similar to Sharpe ratio)
    # with relative quote volume. High values indicate strong risk-adjusted momentum backed by above-average volume.
    df["pc"] = df["close"].pct_change()
    df["vol"] = df["pc"].rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)
    df["ret"] = df["pc"].rolling(n, min_periods=config.min_periods).sum()
    df["cvr"] = (df["ret"] / (df["vol"] + eps)) * (
        df["quote_volume"] / df["quote_volume"].rolling(n, min_periods=config.min_periods).mean()
    )
    df[factor_name] = df["cvr"].rolling(n, min_periods=config.min_periods).mean()
    df.drop(columns=["pc", "vol", "ret", "cvr"], inplace=True)

    return df
