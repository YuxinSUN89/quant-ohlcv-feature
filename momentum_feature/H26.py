def signal(*args):
    # H26 indicator (peak rank-correlation of volume and price rank (duplicate formulation))
    # Formula: H26 = (-1 * ts_max(correlation(ts_rank(VOLUME, 5), ts_rank(HIGH, 5), 5), 3))
    # Same construction as G5 — highest 3-day value of a 5-day volume/high-price rank correlation, negated.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['TSRANK_V_5'] = df['quote_volume'].rolling(5, min_periods=1).apply(lambda x: x.rank(pct=True, method='first').iloc[-1], raw=False)
    df['TSRANK_H_5'] = df['high'].rolling(5, min_periods=1).apply(lambda x: x.rank(pct=True, method='first').iloc[-1], raw=False)
    df['CORR_5'] = df['TSRANK_V_5'].rolling(5).corr(df['TSRANK_H_5'])
    df['TSMAX_3'] = df['CORR_5'].rolling(3).max()
    df['H26'] = df['TSMAX_3'] * -1
    df[factor_name] = df['H26']
    df.drop(columns=['TSRANK_V_5', 'TSRANK_H_5', 'CORR_5', 'TSMAX_3', 'H26'], errors='ignore', inplace=True)

    return df
