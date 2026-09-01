def signal(*args):
    # HighLowPercentileN indicator (prior close's percentile within its own recent range)
    # Formula: HighLowPercentileN = percentile of PREV_CLOSE within the [LOW, HIGH] range of the trailing n days
    # Where the prior close sits, as a percentile, within the [low, high] band spanned over the trailing n days.
    # Near 1 means the prior close was near the top of its recent trading range; near 0 means near the bottom.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[f'highlowpercentilen_1'] = df['high'].shift().rolling(min_periods=1, window=n).max()
    df[f'highlowpercentilen_0'] = df['low'].shift().rolling(min_periods=1, window=n).min()
    df[f'highlowpercentilen_2'] = (df['close'] - df[f'highlowpercentilen_0']) / (df[f'highlowpercentilen_1'] - df[f'highlowpercentilen_0'])
    df[factor_name] = df[f'highlowpercentilen_2']
    df.drop(columns=[f'highlowpercentilen_1', f'highlowpercentilen_0', f'highlowpercentilen_2'], errors='ignore', inplace=True)

    return df
