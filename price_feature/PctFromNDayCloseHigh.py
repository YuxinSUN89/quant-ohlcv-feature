def signal(*args):
    # PctFromNDayCloseHigh indicator (distance from the N-day closing high, percent)
    # Formula: PctFromNDayCloseHigh = PREV_CLOSE's percentage distance from the trailing n-day max CLOSE
    # How far the prior close sits below (or above) the highest close of the trailing n days, as a percentage.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[f'pctfromndayclosehigh_0'] = df['close'].shift().rolling(min_periods=1, window=n).max()
    df[f'pctfromndayclosehigh_2'] = df['close'] / df[f'pctfromndayclosehigh_0'] -1
    df[factor_name] = df[f'pctfromndayclosehigh_2']
    df.drop(columns=[f'pctfromndayclosehigh_0', f'pctfromndayclosehigh_2'], errors='ignore', inplace=True)

    return df
