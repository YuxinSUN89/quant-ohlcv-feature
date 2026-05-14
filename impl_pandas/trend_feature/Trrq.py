import talib as ta


def signal(df, n, factor_name, config):
    # Trrq indicator (Typical Price Regression Return / Normalized Volume)
    # Formula: TP = (HIGH+LOW+CLOSE)/3; NORM_VOL = QUOTE_VOLUME / MA(QUOTE_VOLUME,N)
    #          REG = LINEARREG(TP,N); REG_RETURN = REG.pct_change(N)
    #          result = SUM(REG_RETURN / (NORM_VOL + eps), N)
    # Measures cumulative regression-based price return adjusted by relative volume activity.
    # Low-volume uptrends are amplified; high-volume environments reduce the signal.
    eps = config.eps
    df["tp"] = (df["high"] + df["low"] + df["close"]) / 3
    df["norm_quote_volume"] = df["quote_volume"] / (df["quote_volume"].rolling(n, min_periods=config.min_periods).mean() + config.eps)
    reg_price = ta.LINEARREG(df["tp"], timeperiod=n)
    df["tp_reg_return"] = reg_price.pct_change(n)
    df["tp_reg_return_div_norm_vol"] = df["tp_reg_return"] / (eps + df["norm_quote_volume"])
    df[factor_name] = df["tp_reg_return_div_norm_vol"].rolling(n, min_periods=config.min_periods).sum()

    del df["tp"], df["norm_quote_volume"], df["tp_reg_return"], df["tp_reg_return_div_norm_vol"]

    return df
