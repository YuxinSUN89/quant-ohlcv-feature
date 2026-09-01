eps = 1e-8


def signal(*args):
    # Illiquidity indicator (return-per-unit-of-volume illiquidity ratio)
    # Formula: Illiquidity = abs(PCT_CHG / QUOTE_VOLUME) * 1e8
    # Absolute return divided by quote volume, scaled up for readability (Amihud-style illiquidity, simplified formulation).
    # Higher values mean it took relatively little trading value to move price — i.e. thinner, less liquid conditions.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['pct_chg'] = df['close'].pct_change()
    df['illiquidity_2'] = abs(df['pct_chg'] / (df['quote_volume'] + eps)) * 1e8
    df[factor_name] = df['illiquidity_2']
    df.drop(columns=['illiquidity_2', 'pct_chg'], errors='ignore', inplace=True)

    return df
