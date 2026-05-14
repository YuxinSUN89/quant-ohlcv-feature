import numpy as np
import polars as pl
import talib as ta


def signal(df, n, factor_name, config):
    # Trrq_v3 indicator (Asymmetric volume-adjusted regression return)
    # Formula: TP = (HIGH+LOW+CLOSE)/3; NORM_VOL = QUOTE_VOLUME / MA(QUOTE_VOLUME,N)
    #          REG = LINEARREG(TP,N); REG_CHG = REG.pct_change(N)
    #          SUM_CHG = SUM(REG_CHG,N); SUM_VOL = SUM(NORM_VOL,N)
    #          result = SUM_CHG / (SUM_VOL + eps)  if SUM_CHG > 0 (low-volume uptrend rewarded)
    #                 = SUM_CHG * SUM_VOL           if SUM_CHG <= 0 (high-volume downtrend penalized)
    # Asymmetric treatment: rewards low-volume uptrends and penalizes high-volume downtrends.
    eps = config.eps
    df = df.with_columns(pl.Series("tp", (df["high"] + df["low"] + df["close"]) / 3))
    df = df.with_columns(
        pl.Series(
            "normalized_quote_volume",
            df["quote_volume"] / df["quote_volume"].rolling_mean(n, min_samples=config.min_periods),
        ).fill_nan(None)
    )
    reg_price = ta.LINEARREG(df["tp"], timeperiod=n)
    df = df.with_columns(pl.Series("tp_reg_price_change", reg_price.pct_change(n)).fill_nan(None))
    df = df.with_columns(
        pl.Series("tp_reg_price_change_sum", df["tp_reg_price_change"].rolling_sum(n, min_samples=config.min_periods))
    )
    df = df.with_columns(
        pl.Series(
            "normalized_quote_volume_sum", df["normalized_quote_volume"].rolling_sum(n, min_samples=config.min_periods)
        )
    )
    df = df.with_columns(
        pl.Series(
            factor_name,
            np.where(
                df["tp_reg_price_change_sum"] > 0,
                df["tp_reg_price_change_sum"]
                / (eps + df["normalized_quote_volume_sum"]),  # if rising, consistent with low-volume uptrend
                df["tp_reg_price_change_sum"] * df["normalized_quote_volume_sum"],
            ),
        )
    )  # if falling, consistent with high-volume downtrend

    df = df.drop(
        [
            "tp",
            "normalized_quote_volume",
            "tp_reg_price_change",
            "tp_reg_price_change_sum",
            "normalized_quote_volume_sum",
        ]
    )

    return df
