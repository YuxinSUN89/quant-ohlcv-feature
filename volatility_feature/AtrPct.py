def signal(df, n, factor_name, config):
    # AtrPct indicator (ATR N-period percentage change)
    # Formula: ATR = MA(TR, N); result = ATR.pct_change(N)
    # Measures the rate of change of ATR over N periods. Positive values indicate volatility is
    # expanding; negative values indicate volatility is contracting relative to N periods ago.
    df["close_1"] = df["close"].shift()
    tr = df[["high", "low", "close_1"]].max(axis=1) - df[["high", "low", "close_1"]].min(axis=1)
    atr = tr.rolling(n, min_periods=config.min_periods).mean()
    df[factor_name] = atr.pct_change(n)

    del df["close_1"]

    return df
