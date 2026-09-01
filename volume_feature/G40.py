def signal(*args):
    # G40 indicator (up-day vs. down-day volume ratio)
    # Formula: G40 = SUM((CLOSE>DELAY(CLOSE,1)?VOLUME:0),26)/SUM((CLOSE<=DELAY(CLOSE,1)?VOLUME:0),26)*100
    # Ratio of volume summed on up days to volume summed on down/flat days over 26 periods, scaled to 100.
    # Above 100 means volume has concentrated on up days; below 100 means it has concentrated on down days.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = 26
    df['condition'] = 0.0
    df['alpha40_01'] = 0.0
    df['alpha40_02'] = 0.0
    df.loc[df['close'] > df['close'].shift(), 'condition'] = 1
    df.loc[df['condition'] == 1, 'alpha40_01'] = df['volume']
    df.loc[df['condition'] == 0, 'alpha40_02'] = df['volume']
    df['G40'] = df['alpha40_01'].rolling(n).sum() / df['alpha40_02'].rolling(n).sum() * 100
    df[factor_name] = df['G40']
    df.drop(columns=['condition', 'alpha40_01', 'alpha40_02', 'G40'], errors='ignore', inplace=True)

    return df
