def signal(df, n, factor_name, config):
    # Uos indicator (Ultimate Oscillator — triple timeframe)
    # Formula: TH = MAX(HIGH, REF(CLOSE,1)); TL = MIN(LOW, REF(CLOSE,1)); TR = TH - TL; XR = CLOSE - TL
    #          BP_M = SUM(XR,M)/SUM(TR,M); BP_N = SUM(XR,N)/SUM(TR,N); BP_O = SUM(XR,O)/SUM(TR,O)
    #          UOS = 100 * (BP_M*N*O + BP_N*M*O + BP_O*M*N) / (M*N + M*O + N*O)
    #          where M=N, N=2N, O=4N (three timeframes)
    # The Ultimate Oscillator combines buying pressure across three timeframes (short, medium, long).
    # Range [0, 100]. Above 70 = overbought; below 30 = oversold.
    M = n
    N = 2 * n
    O = 4 * n  # noqa: E741
    df["ref_close"] = df["close"].shift(1)
    df["TH"] = df[["high", "ref_close"]].max(axis=1)
    df["TL"] = df[["low", "ref_close"]].min(axis=1)
    df["TR"] = df["TH"] - df["TL"]
    df["XR"] = df["close"] - df["TL"]
    df["XRM"] = (
        df["XR"].rolling(M, min_periods=config.min_periods).sum()
        / df["TR"].rolling(M, min_periods=config.min_periods).sum()
    )
    df["XRN"] = (
        df["XR"].rolling(N, min_periods=config.min_periods).sum()
        / df["TR"].rolling(N, min_periods=config.min_periods).sum()
    )
    df["XRO"] = (
        df["XR"].rolling(O, min_periods=config.min_periods).sum()
        / df["TR"].rolling(O, min_periods=config.min_periods).sum()
    )
    df[factor_name] = 100 * (df["XRM"] * N * O + df["XRN"] * M * O + df["XRO"] * M * N) / (M * N + M * O + N * O)

    # remove redundant columns
    del df["ref_close"], df["TH"], df["TL"], df["TR"], df["XR"]
    del df["XRM"], df["XRN"], df["XRO"]

    return df
