def signal(*args):
    # PctFromNDayHigh indicator (distance from the N-day high, percent)
    # Formula: PctFromNDayHigh = PREV_CLOSE's percentage distance from the trailing n-day HIGH
    # How far the prior close sits below (or above) the highest high of the trailing n days, as a percentage.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[f'pctfromndayhigh_0'] = df['high'].shift().rolling(min_periods=1, window=n).max()
    df[f'pctfromndayhigh_3'] = df['close'] / df[f'pctfromndayhigh_0'] -1
    df[factor_name] = df[f'pctfromndayhigh_3']
    df.drop(columns=[f'pctfromndayhigh_0', f'pctfromndayhigh_3'], errors='ignore', inplace=True)

    return df
