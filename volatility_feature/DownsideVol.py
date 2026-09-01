def signal(*args):
    # DownsideVol indicator (volatility of down days)
    # Formula: DownsideVol = STD(PCT_CHG, n) computed over days where PCT_CHG < 0
    # Rolling std of daily returns, computed only over days with a negative return.
    # Isolates how choppy the market has been specifically during selloffs.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['pct_chg'] = df['close'].pct_change()
    n = int(n)
    df['downsidevol_2'] = df['pct_chg'].apply(lambda x: x if x < 0 else 0)
    df[f'downsidevol_0'] = df['downsidevol_2'].rolling(n).std()
    df[factor_name] = df[f'downsidevol_0']
    df.drop(columns=['downsidevol_2', f'downsidevol_0', 'pct_chg'], errors='ignore', inplace=True)

    return df
