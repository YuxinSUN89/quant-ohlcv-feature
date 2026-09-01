def signal(*args):
    # RetRebound indicator (short vs. long return rebound)
    # Formula: RetRebound = CLOSE.pct_change(n) - CLOSE.pct_change(2*n)
    # Difference between the n-day return and the 2n-day return.
    # Positive values mean recent (n-day) performance is outpacing the longer (2n-day) trend — a rebound signal.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[f'retrebound_0'] = df['close'].pct_change(n) - df['close'].pct_change(2*n)
    df[factor_name] = df[f'retrebound_0']
    df.drop(columns=[f'retrebound_0'], errors='ignore', inplace=True)

    return df
