import pandas as pd

eps = 1e-8


def signal(*args):
    # G68 indicator (midpoint-move range/volume oscillator)
    # Formula: G68 = SMA(((HIGH+LOW)/2-(DELAY(HIGH,1)+DELAY(LOW,1))/2)*(HIGH-LOW)/VOLUME,15,2)
    # Smoothed measure of the change in the (high+low)/2 midpoint times the day's range, normalized by volume, 15-period.
    # Captures whether price displacement is happening on comparatively light volume (larger magnitude) or heavy volume (smaller magnitude).
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['factor_g68'] = ((df['high'] + df['low']) / 2 - (df['high'].shift() + df['low'].shift()) / 2) * (df['high'] - df['low'] + eps) / (df['quote_volume'] + eps)
    df['G68'] = pd.DataFrame.ewm(df['factor_g68'], alpha=2.0 / 15).mean()
    df[factor_name] = df['G68']
    df.drop(columns=['factor_g68', 'G68'], errors='ignore', inplace=True)

    return df
