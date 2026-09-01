def signal(*args):
    # BreakNDayHigh indicator (N-day high breakout flag)
    # Formula: BreakNDayHigh = whether PREV_CLOSE is above the highest HIGH of the trailing N days
    # 1 if the prior close exceeds the highest high of the trailing N days, 0 otherwise.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[f'breakndayhigh_0'] = df['high'].shift().rolling(min_periods=1, window=n).max()
    df[f'breakndayhigh_2'] = (df['close'] > df[f'breakndayhigh_0']).astype(int)
    df[factor_name] = df[f'breakndayhigh_2']
    df.drop(columns=[f'breakndayhigh_0', f'breakndayhigh_2'], errors='ignore', inplace=True)

    return df
