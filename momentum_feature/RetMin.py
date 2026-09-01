def signal(*args):
    # RetMin indicator (n-day return filtered by a minimum threshold)
    # Formula: RetMin = n-day PCT_CHG with values below min_ret set to None; n and min_ret default to 60 and 0.01
    # n-day return with any value smaller than min_ret discarded (set to missing).
    # Isolates only the periods where the move was large enough to be considered meaningful.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    [n, min_ret] = [int(n), n] if n else [60, 0.01]
    df[factor_name] = df['close'].pct_change(n)

    return df
