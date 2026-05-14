import numpy as np
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
    df["tp"] = (df["high"] + df["low"] + df["close"]) / 3
    df["normalized_quote_volume"] = (
        df["quote_volume"] / (df["quote_volume"].rolling(n, min_periods=config.min_periods).mean() + config.eps)
    )
    reg_price = ta.LINEARREG(df["tp"], timeperiod=n)
    df["tp_reg_price_change"] = reg_price.pct_change(n)
    df["tp_reg_price_change_sum"] = df["tp_reg_price_change"].rolling(n, min_periods=config.min_periods).sum()
    df["normalized_quote_volume_sum"] = df["normalized_quote_volume"].rolling(n, min_periods=config.min_periods).sum()
    df[factor_name] = np.where(
        df["tp_reg_price_change_sum"] > 0,
        df["tp_reg_price_change_sum"]
        / (eps + df["normalized_quote_volume_sum"]),  # if rising, consistent with low-volume uptrend
        df["tp_reg_price_change_sum"] * df["normalized_quote_volume_sum"],
    )  # if falling, consistent with high-volume downtrend

    del (
        df["tp"],
        df["normalized_quote_volume"],
        df["tp_reg_price_change"],
        df["tp_reg_price_change_sum"],
        df["normalized_quote_volume_sum"],
    )

    return df
