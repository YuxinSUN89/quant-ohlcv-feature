def signal(*args):
    # CurrentDrawdown indicator (close relative to the rolling high)
    # Formula: CurrentDrawdown = CLOSE / MAX(HIGH, n)
    # Current close divided by the n-day rolling maximum of high.
    # Below 1 means price is currently under its recent peak; the size of the gap is the current drawdown.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[f'currentdrawdown_2'] = df['high'].rolling(n).max()
    df[f'currentdrawdown_0'] = df['close'] / df[f'currentdrawdown_2']
    df[factor_name] = df[f'currentdrawdown_0']
    df.drop(columns=[f'currentdrawdown_2', f'currentdrawdown_0'], errors='ignore', inplace=True)

    return df
