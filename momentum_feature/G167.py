def signal(*args):
    # G167 indicator (12-day sum of up-move magnitude)
    # Formula: G167 = SUM((CLOSE - DELAY(CLOSE, 1) > 0?CLOSE-DELAY(CLOSE, 1): 0), 12)
    # Sum of the size of up days only (0 on down/flat days) over 12 periods.
    # Larger values indicate heavier recent buying pressure (mirror of G129).
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df.loc[df['close'] - df['close'].shift(1) > 0, 'G167'] = df['close'] - df['close'].shift(1)
    df.loc[df['close'] - df['close'].shift(1) <= 0, 'G167'] = 0
    df['G167'] = df['G167'].rolling(12, min_periods=1).sum()
    df[factor_name] = df['G167']
    df.drop(columns=['G167'], errors='ignore', inplace=True)

    return df
