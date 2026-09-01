def signal(*args):
    # PosRet indicator (average of positive returns)
    # Formula: PosRet = MA(PCT_CHG where PCT_CHG > 0 else 0, n)
    # n-day average return, counting only days with a positive return (0 on down/flat days).
    # Captures the typical size of recent up moves, independent of how often they occur.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)

    df['pct_chg'] = df['close'].pct_change()
    df['pos_ret'] = df['pct_chg'].where(df['pct_chg'] > 0, 0)
    df[factor_name] = df['pos_ret'].rolling(n).mean()
    df.drop(columns=['pct_chg', 'pos_ret'], errors='ignore', inplace=True)

    return df
