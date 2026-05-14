import polars as pl


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
    df = df.with_columns(pl.Series("ref_close", df["close"].shift(1)))
    df = df.with_columns(TH=pl.max_horizontal([pl.col("high"), pl.col("ref_close")]))
    df = df.with_columns(TL=pl.min_horizontal([pl.col("low"), pl.col("ref_close")]))
    df = df.with_columns(pl.Series("TR", df["TH"] - df["TL"]))
    df = df.with_columns(pl.Series("XR", df["close"] - df["TL"]))
    df = df.with_columns(
        pl.Series(
            "XRM",
            (
                df["XR"].rolling_sum(M, min_samples=config.min_periods)
                / df["TR"].rolling_sum(M, min_samples=config.min_periods)
            ),
        ).fill_nan(None)
    )
    df = df.with_columns(
        pl.Series(
            "XRN",
            (
                df["XR"].rolling_sum(N, min_samples=config.min_periods)
                / df["TR"].rolling_sum(N, min_samples=config.min_periods)
            ),
        ).fill_nan(None)
    )
    df = df.with_columns(
        pl.Series(
            "XRO",
            (
                df["XR"].rolling_sum(O, min_samples=config.min_periods)
                / df["TR"].rolling_sum(O, min_samples=config.min_periods)
            ),
        ).fill_nan(None)
    )
    df = df.with_columns(
        pl.Series(
            factor_name, 100 * (df["XRM"] * N * O + df["XRN"] * M * O + df["XRO"] * M * N) / (M * N + M * O + N * O)
        )
    )

    # remove redundant columns
    df = df.drop(["ref_close", "TH", "TL", "TR", "XR"])
    df = df.drop(["XRM", "XRN", "XRO"])

    return df
