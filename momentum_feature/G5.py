import pandas as pd


def signal(*args):
    # G5 indicator (peak rank-correlation of volume and price rank)
    # Formula: G5 = -1 * TSMAX(CORR(TSRANK(VOLUME, 5), TSRANK(HIGH, 5), 5), 3)
    # Highest 3-day value of a 5-day rolling rank-correlation between volume rank and high-price rank, negated.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n =  3
    TS_RANK = lambda x: pd.Series(x).rank().iloc[-1]
    df['G5'] = -1 * (((df['volume'].rolling(5).apply(TS_RANK)).rolling(5).corr(df['high'].rolling(5).apply(TS_RANK)))
                     .rolling(n, min_periods=1).max())
    df[factor_name] = df['G5']
    df.drop(columns=['G5'], errors='ignore', inplace=True)

    return df
