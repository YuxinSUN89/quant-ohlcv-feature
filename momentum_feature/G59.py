def signal(*args):
    # G59 indicator (20-day sum of close deviation from the prior extreme)
    # Formula: G59 = SUM((CLOSE=DELAY(CLOSE,1)?0:CLOSE-(CLOSE>DELAY(CLOSE,1)?MIN(LOW,DELAY(CLOSE,1)):MAX(HIGH,DELAY(CLOSE,1)))),20)
    # Same construction as G3 (accumulate close vs. the relevant prior extreme) but over a 20-day window.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    condition = df["close"] == df["close"].shift(1)
    condition1 = df["close"] > df["close"].shift(1)
    condition2 = df["close"] < df["close"].shift(1)
    df.loc[condition, 'G59'] = 0
    df.loc[condition1, 'G59'] = (df["close"] - (df[["low", "close"]].min(axis=1)).shift(1)).rolling(20, min_periods=1).sum()
    df.loc[condition2, 'G59'] = (df["close"] - (df[["high", "close"]].max(axis=1)).shift(1)).rolling(20, min_periods=1).sum()
    df[factor_name] = df['G59']
    df.drop(columns=['G59'], errors='ignore', inplace=True)

    return df
