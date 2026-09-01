def signal(*args):
    # Sharpe indicator (rolling Sharpe-style ratio of returns)
    # Formula: Sharpe = MA(PCT_CHG, n) / STD(PCT_CHG, n)
    # n-day mean return divided by n-day return std.
    # Higher values indicate more consistent, better risk-adjusted directional performance over the window.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['pct_chg'] = df['close'].pct_change()
    n = int(n)
    df[f'sharpe_2'] = df['pct_chg'].rolling(n).mean()
    df[f'sharpe_3'] = df['pct_chg'].rolling(n).std()
    df[f'sharpe_0'] = df[f'sharpe_2'] / df[f'sharpe_3']
    df[factor_name] = df[f'sharpe_0']
    df.drop(columns=[f'sharpe_2', f'sharpe_3', f'sharpe_0', 'pct_chg'], errors='ignore', inplace=True)

    return df
