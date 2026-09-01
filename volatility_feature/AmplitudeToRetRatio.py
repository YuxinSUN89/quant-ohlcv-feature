def signal(*args):
    # AmplitudeToRetRatio indicator (return relative to amplitude)
    # Formula: AmplitudeToRetRatio = CLOSE.pct_change() / (HIGH / LOW - 1)
    # Today's percentage return divided by today's high/low amplitude.
    # Values near the extremes mean the day's net move captured most of its own trading range; values near 0 mean a wide range with little net progress.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    # n = int(n)
    df['amplitudetoretratio_5'] = df['close'].pct_change()
    df['amplitudetoretratio_0'] = df['high']/df['low'] - 1
    df[f'amplitudetoretratio_1'] = df['amplitudetoretratio_0']/(df['amplitudetoretratio_5'] + 1e-8)
    df[factor_name] = df[f'amplitudetoretratio_1']
    df.drop(columns=['amplitudetoretratio_5', 'amplitudetoretratio_0', f'amplitudetoretratio_1'], errors='ignore', inplace=True)

    return df
