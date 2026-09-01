def signal(*args):
    # UpperShadow indicator (upper candle wick, normalized)
    # Formula: UpperShadow = (HIGH - MAX(OPEN, CLOSE)) / PREV_CLOSE
    # Distance from the day's high to the higher of open/close, scaled by the prior close.
    # Larger values indicate a longer upper wick — sellers pushed price back down from an intraday high.
    df = args[0]
    n = args[1]
    factor_name = args[2]

    df[factor_name] = (df['high'] - df[['open', 'close']].max(axis=1)) / df['close'].shift()

    return df
