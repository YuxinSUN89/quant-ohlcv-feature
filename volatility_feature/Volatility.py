def signal(*args):
    # Volatility indicator (n-day return volatility)
    # Formula: n-day std of PCT_CHG
    # Rolling n-day standard deviation of daily returns.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['pct_chg'] = df['close'].pct_change()
    n = int(n)
    df[factor_name] = df['pct_chg'].rolling(n).std()
    df.drop(columns=['pct_chg'], errors='ignore', inplace=True)

    return df
