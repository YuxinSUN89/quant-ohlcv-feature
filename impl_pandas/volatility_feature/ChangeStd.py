def signal(df, n, factor_name, config):
    # ChangeStd indicator (N-period return × rolling return std)
    # Formula: RTN = CLOSE.pct_change(); result = CLOSE.pct_change(N) * STD(RTN, N)
    # Combines directional momentum (N-period return) with recent volatility (rolling std of 1-period returns).
    # Acts as a risk-adjusted momentum measure: large returns in high-volatility environments are discounted.
    rtn = df["close"].pct_change()
    df[factor_name] = df["close"].pct_change(n) * rtn.rolling(n, min_periods=config.min_periods).std(ddof=config.ddof)

    return df
