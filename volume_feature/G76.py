eps = 1e-8


def signal(*args):
    # G76 indicator (coefficient of variation of return-per-volume)
    # Formula: G76 = STD(ABS((CLOSE/DELAY(CLOSE,1)-1))/VOLUME,20)/MEAN(ABS((CLOSE/DELAY(CLOSE,1)-1))/VOLUME,20)
    # Std of |return|/volume divided by the mean of |return|/volume, over 20 days.
    # Higher values mean the market-impact-per-share has been unusually inconsistent recently.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G76'] = ((df['close'] / df['close'].shift() - 1).abs() / (df['quote_volume'] + eps)).rolling(20, min_periods=1).std() / ( (df['close'] / df['close'].shift() - 1).abs() / (df['quote_volume'] + eps)).rolling(20, min_periods=1).mean()
    df[factor_name] = df['G76']
    df.drop(columns=['G76'], errors='ignore', inplace=True)

    return df
