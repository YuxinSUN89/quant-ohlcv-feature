def signal(*args):
    # G188 indicator (range relative to its own smoothed trend, in percent)
    # Formula: G188 = ((HIGH-LOW–SMA(HIGH-LOW,11,2))/SMA(HIGH-LOW,11,2))*100
    # Percentage deviation of the current HIGH-LOW range from its own 11-period smoothed average.
    # Positive values flag a range expansion versus the recent trend; negative values flag contraction.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df["HIGH_LOW_DIFF"] = df["high"] - df["low"]
    df["SMA_11_2_VALUE"] = df["HIGH_LOW_DIFF"].ewm(alpha=2.0 / 11, adjust=False).mean()
    df['G188'] = ((df["HIGH_LOW_DIFF"] - df["SMA_11_2_VALUE"]) / df["SMA_11_2_VALUE"]) * 100
    df[factor_name] = df['G188']
    df.drop(columns=["HIGH_LOW_DIFF", "SMA_11_2_VALUE", 'G188'], errors='ignore', inplace=True)

    return df
