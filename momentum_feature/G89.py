def signal(*args):
    # G89 indicator (double MACD-style oscillator)
    # Formula: G89 = 2*(SMA(CLOSE,13,2)-SMA(CLOSE,27,2)-SMA(SMA(CLOSE,13,2)-SMA(CLOSE,27,2),10,2))
    # Twice the MACD-style histogram (13 vs. 27-period smoothed close, minus its own 10-period signal line).
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['DIF'] = df['close'].ewm(alpha=2 / 13, adjust=False).mean() - df['close'].ewm(alpha=2 / 27,adjust=False).mean()
    df['G89'] = 2 * (df['DIF'] - df['DIF'].ewm(alpha=2 / 10, adjust=False).mean())
    df[factor_name] = df['G89']
    df.drop(columns=['DIF', 'G89'], errors='ignore', inplace=True)

    return df
