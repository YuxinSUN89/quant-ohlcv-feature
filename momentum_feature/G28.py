def signal(*args):
    # G28 indicator (double-smoothed stochastic oscillator (KDJ-style))
    # Formula: G28 = 3*SMA((CLOSE-TSMIN(LOW,9))/(TSMAX(HIGH,9)-TSMIN(LOW,9))*100,3,1)-2*SMA(SMA((CLOSE-TSMIN(LOW,9))/(MAX(HIGH,9)-TSMAX(LOW,9))*100,3,1),3,1)
    # A fast-minus-slow blend of a smoothed %K-style stochastic measure over a 9-day window, similar to the KDJ family.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df["mid"] = (df["close"] - df["low"].rolling(9).min()) / ( df["high"].rolling(9).max() - df["low"].rolling(9).min()) * 100
    df["ewm"] = df["mid"].ewm(alpha=1 / 3.0, adjust=False).mean()
    df["G28"] = 3 * df["ewm"] - 2 * df["ewm"].ewm(alpha=1 / 3.0, adjust=False).mean()
    df[factor_name] = df['G28']
    df.drop(columns=["mid", "ewm", "G28"], errors='ignore', inplace=True)

    return df
