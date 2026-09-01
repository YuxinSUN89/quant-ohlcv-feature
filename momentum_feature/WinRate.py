def signal(*args):
    # WinRate indicator (win rate)
    # Formula: WinRate = fraction of days within n with PCT_CHG > 0
    # Fraction of the last n days with a positive return.
    # Above 0.5 means more days were winners than losers over the window.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['pct_chg'] = df['close'].pct_change()
    n = int(n)
    df[f'winrate_1'] = (df['pct_chg'] > 0).rolling(n, min_periods=1).mean()
    df[factor_name] = df[f'winrate_1']
    df.drop(columns=[f'winrate_1', 'pct_chg'], errors='ignore', inplace=True)

    return df
