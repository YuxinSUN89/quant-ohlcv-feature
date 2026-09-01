def signal(*args):
    # VBoll indicator (Bollinger-style breakout count on quote volume)
    # Formula: upper = MA(QUOTE_VOLUME, n) + 2 * STD(QUOTE_VOLUME, n), lower = MA(QUOTE_VOLUME, n) - 2 * STD(QUOTE_VOLUME, n)
    # Counts, over n days, how often trading value has broken above or below its own Bollinger Bands.
    # Positive counts mean volume has repeatedly surged above its band; negative counts mean it has repeatedly collapsed below it.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    n = int(n)
    df['mean'] = df['quote_volume'].rolling(n).mean()
    df['std'] = df['quote_volume'].rolling(n).std(ddof=0)
    df['upper'] = df['mean'] + 2 * df['std']
    df['lower'] = df['mean'] - 2 * df['std']
    df['count'] = 0.0
    df.loc[df['quote_volume'] > df['upper'], 'count'] = 1
    df.loc[df['quote_volume'] < df['lower'], 'count'] = -1
    df[f'VBoll_{n}'] = df['count'].rolling(n).sum()
    df[factor_name] = df[f'VBoll_{n}']
    df.drop(columns=['mean', 'std', 'upper', 'lower', 'count', f'VBoll_{n}'], errors='ignore', inplace=True)

    return df
