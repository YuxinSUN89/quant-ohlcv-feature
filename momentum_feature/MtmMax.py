def signal(*args):
    # MtmMax indicator (MTM vs rolling max of MTM)
    # Formula: MTM = CLOSE/REF(CLOSE,N)-1; result = MTM - MAX(MTM, N).shift(1)
    # Measures how the current N-period momentum compares to the maximum momentum achieved over the past N periods.
    # Negative values indicate current momentum is below recent peak (momentum fading); 0 indicates new high.
    df = args[0]
    n = args[1]
    factor_name = args[2]

    df['mtm'] = df['close'] / df['close'].shift(n) - 1
    df['up'] = df['mtm'].rolling(window=n).max().shift(1)
    df[factor_name] = df['mtm'] - df['up']

    del df['mtm']
    del df['up']

    return df
