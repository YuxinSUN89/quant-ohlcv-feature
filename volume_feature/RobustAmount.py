eps = 1e-8


def signal(*args):
    # RobustAmount indicator (traded-value mean-to-volatility ratio)
    # Formula: RobustAmount = MA(QUOTE_VOLUME, n) / STD(QUOTE_VOLUME, n)
    # n-day mean of quote volume divided by its own n-day standard deviation.
    # Higher values indicate trading value has been large and steady; lower values indicate it has been erratic relative to its own level.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    df[f'robustamount_1'] = df['quote_volume'].rolling(n).mean() / (df['quote_volume'] + eps).rolling(n).std()
    df[factor_name] = df[f'robustamount_1']
    df.drop(columns=[f'robustamount_1'], errors='ignore', inplace=True)

    return df
