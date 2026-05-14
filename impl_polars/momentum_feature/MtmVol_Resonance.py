import polars as pl


def signal(df, n, factor_name, config):
    # MtmVol_Resonance indicator (MTM mean × volume change mean)
    # Formula: MTM_MEAN = MA(CLOSE/REF(CLOSE,N)-1, N)
    #          VOL_CHG = QUOTE_VOLUME / MA(QUOTE_VOLUME,N); VOL_CHG_MEAN = MA(VOL_CHG, N)
    #          result = MTM_MEAN * VOL_CHG_MEAN
    # Resonance between price momentum and relative volume activity.
    # High values indicate sustained price momentum coinciding with above-average trading volume.
    df = df.with_columns(pl.Series("mtm", df["close"] / (df["close"].shift(n) + config.eps) - 1))
    df = df.with_columns(pl.Series("mtm_mean", df["mtm"].rolling_mean(n, min_samples=config.min_periods)))

    df = df.with_columns(
        pl.Series("quote_volume_mean", df["quote_volume"].rolling_mean(n, min_samples=config.min_periods))
    )
    df = df.with_columns(pl.Series("quote_volume_change", (df["quote_volume"] / (df["quote_volume_mean"] + config.eps))))
    df = df.with_columns(
        pl.Series("quote_volume_change_mean", df["quote_volume_change"].rolling_mean(n, min_samples=config.min_periods))
    )

    df = df.with_columns(pl.Series(factor_name, df["mtm_mean"] * df["quote_volume_change_mean"]))

    drop_col = ["mtm", "mtm_mean", "quote_volume_mean", "quote_volume_change", "quote_volume_change_mean"]
    df = df.drop(drop_col)

    return df
