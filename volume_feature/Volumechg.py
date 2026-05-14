def signal(df, n, factor_name, config):
    # Volumechg indicator (Direction-weighted Volume Change rolling max)
    # Formula: DIRECTION = +1 if CLOSE > REF(CLOSE,1) else -1
    #          VOL_CHANGE = (QUOTE_VOLUME / REF(QUOTE_VOLUME,1)) * DIRECTION
    #          result = ROLLING_MAX(VOL_CHANGE, N)
    # Captures the maximum directional volume change over N periods. Positive values indicate
    # that large volume surges occurred on up-days; negative values indicate surges on down-days.
    df["hourly_price_change"] = df["close"].pct_change(1)
    df.loc[df["hourly_price_change"] > 0, "direction"] = 1
    df.loc[df["hourly_price_change"] < 0, "direction"] = -1
    df["volume_change"] = df["quote_volume"] / df["quote_volume"].shift(1) * df["direction"]
    df[factor_name] = df["volume_change"].rolling(n, min_periods=config.min_periods).max()

    return df
