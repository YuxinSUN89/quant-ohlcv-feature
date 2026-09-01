def signal(*args):
    # NegRet indicator (average of negative returns)
    # Formula: NegRet = MA(PCT_CHG where PCT_CHG <= 0 else 0, n)
    # n-day average return, counting only days with a non-positive return (0 on up days).
    # Captures the typical size of recent down moves, independent of how often they occur.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)

    df['pct_chg'] = df['close'].pct_change()
    df['neg_ret'] = df['pct_chg'].where(df['pct_chg'] <= 0, 0)
    df[factor_name] = df['neg_ret'].rolling(n).mean()
    df.drop(columns=['pct_chg', 'neg_ret'], errors='ignore', inplace=True)

    return df
