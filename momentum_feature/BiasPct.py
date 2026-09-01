def signal(*args):
    # BiasPct indicator (rate of change of Bias)
    # Formula: BiasPct = m-day rate of change of Bias_n; m defaults to 10
    # Measures how much the underlying Bias_n reading has itself changed over the last m days.
    # Captures acceleration/deceleration of the mean-reversion signal rather than its level.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    n = int(n)
    m = int(10)
    df[f'MA_{n}'] = df['close'].rolling(n).mean()
    df[f"Bias_{n}"] = (df["close"] - df[f'MA_{n}']) / df[f'MA_{n}']
    df[f"BiasPct_{n}_{m}"] = df[f"Bias_{n}"].pct_change(m)
    df[factor_name] = df[f"BiasPct_{n}_{m}"]
    df.drop(columns=[f'MA_{n}', f"Bias_{n}", f"BiasPct_{n}_{m}"], errors='ignore', inplace=True)

    return df
