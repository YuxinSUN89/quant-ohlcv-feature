def signal(*args):
    '''
    Build using hint as the B-selection factor
    '''
    df = args[0]
    n = args[1]
    factor_name = args[2]
    # ==============================================================

    df['mtm'] = df['high'] / df['high'].shift(n) - 1
    df['mtm_mean'] = df['mtm'].rolling(window=n, min_periods=1).mean()
    df['ma'] = df['close'].rolling(n, min_periods=1).mean()
    df['cm'] = df['close'] / df['ma']
    df[factor_name] = (df['mtm_mean'] - df['cm']) / df['cm']

    del df['mtm']
    del df['mtm_mean']
    del df['ma']
    del df['cm']

    return df
