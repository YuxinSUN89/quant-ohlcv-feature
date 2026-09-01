def signal(*args):
    # UpsideVol indicator (volatility of up days)
    # Formula: UpsideVol = STD(PCT_CHG, n) computed over days where PCT_CHG > 0
    # Rolling std of daily returns, computed only over days with a positive return.
    # Isolates how choppy the market has been specifically during rallies.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['pct_chg'] = df['close'].pct_change()
    n = int(n)
    df['upsidevol_1'] = df['pct_chg'].apply(lambda x: x if x > 0 else 0)
    df[f'upsidevol_0'] = df['upsidevol_1'].rolling(n).std()
    df[factor_name] = df[f'upsidevol_0']
    df.drop(columns=['upsidevol_1', f'upsidevol_0', 'pct_chg'], errors='ignore', inplace=True)

    return df
