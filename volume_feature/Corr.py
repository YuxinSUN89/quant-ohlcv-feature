def signal(*args):
    # Corr indicator (return/volume correlation)
    # Formula: Corr = n-day correlation between PCT_CHG and VOLUME
    # Rolling correlation between daily returns and traded volume.
    # Positive values mean rallies tend to come on higher volume (and selloffs on lower volume); negative values mean the opposite.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['pct_chg'] = df['close'].pct_change()
    n = int(n)
    df[f'Corr_{n}'] = df['pct_chg'].rolling(n).corr(df['volume'])
    df[factor_name] = df[f'Corr_{n}']
    df.drop(columns=[f'Corr_{n}', 'pct_chg'], errors='ignore', inplace=True)

    return df
