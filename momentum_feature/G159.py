def signal(*args):
    # G159 indicator (multi-horizon close-location-value composite)
    # Formula: G159 = ((CLOSE - SUM(MIN(LOW,DELAY(CLOSE,1)),6))/SUM(MAX(HGIH,DELAY(CLOSE,1)) - MIN(LOW,DELAY(CLOSE,1)),6)*12*24+(CLOSE - SUM(MIN(LOW,DELAY(CLOSE,1)),12))/SUM(MAX(HGIH,DELAY(CLOSE,1)) - MIN(LOW,DELAY(CLOSE,1)),12)*6*24+(CLOSE - SUM(MIN(LOW,DELAY(CLOSE,1)),24))/SUM(MAX(HGIH,DELAY(CLOSE,1)) - MIN(LOW,DELAY(CLOSE,1)),24)*6*24)*100/(6*12+6*24+12*24)
    # Blends CLV-style close-vs-range positioning across 6-, 12- and 24-day windows into one weighted score.
    # Higher values mean close has been sitting persistently near the top of its recent range across horizons.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G159_delay'] = df['close'].shift(1)
    df['G159_min_value'] = df.loc[:, ['low', 'G159_delay']].min(axis=1)
    df['G159_max_value'] = df.loc[:, ['high', 'G159_delay']].max(axis=1)
    df['G159_sum_min_6'] = df['G159_min_value'].rolling(6).sum()
    df['G159_sum_min_12'] = df['G159_min_value'].rolling(12).sum()
    df['G159_sum_min_24'] = df['G159_min_value'].rolling(24).sum()
    df['G159_sum_6'] = (df['G159_max_value'] - df['G159_min_value']).rolling(6).sum()
    df['G159_sum_12'] = (df['G159_max_value'] - df['G159_min_value']).rolling(12).sum()
    df['G159_sum_24'] = (df['G159_max_value'] - df['G159_min_value']).rolling(24).sum()
    df['G159'] = ((df['close'] - df['G159_sum_min_6']) / df['G159_sum_6'] * 12 * 24 + ( df['close'] - df['G159_sum_min_12']) / df['G159_sum_12'] * 6 * 24 + ( df['close'] - df['G159_sum_min_24']) / df['G159_sum_24'] * 6 * 24) * 100 / ( 6 * 12 + 6 * 24 + 12 * 24)
    df[factor_name] = df['G159']
    df.drop(columns=['G159_delay', 'G159_min_value', 'G159_max_value', 'G159_sum_min_6', 'G159_sum_min_12', 'G159_sum_min_24', 'G159_sum_6', 'G159_sum_12', 'G159_sum_24', 'G159'], errors='ignore', inplace=True)

    return df
