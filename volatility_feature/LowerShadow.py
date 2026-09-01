def signal(*args):
    # LowerShadow indicator (lower candle wick, normalized)
    # Formula: LowerShadow = (LOW - MIN(OPEN, CLOSE)) / PREV_CLOSE
    # Distance from the day's low to the lower of open/close, scaled by the prior close.
    # Larger values indicate a longer lower wick — buyers stepped in and pushed price back up from an intraday low.
    df = args[0]
    n = args[1]
    factor_name = args[2]

    df[factor_name] = (df['low'] - df[['open', 'close']].min(axis=1)) / df['close'].shift()

    return df
