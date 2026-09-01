def signal(*args):
    # G158 indicator (close position within a smoothed price channel)
    # Formula: G158 = ((HIGH-SMA(CLOSE,15,2))-(LOW-SMA(CLOSE,15,2)))/CLOSE
    # Compares high and low to a 15-period smoothed close, scaled by close.
    # Captures how wide the current bar's range sits relative to the smoothed trend price.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G158'] = ((df['high'] - df['close'].ewm(alpha=2 / 15, adjust=False).mean()) - (df['low'] - df['close'].ewm(alpha=2 / 15, adjust=False).mean())) / df['close']
    df[factor_name] = df['G158']
    df.drop(columns=['G158'], errors='ignore', inplace=True)

    return df
