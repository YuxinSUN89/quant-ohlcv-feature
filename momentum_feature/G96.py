def signal(*args):
    # G96 indicator (double-smoothed stochastic %K)
    # Formula: G96 = SMA(SMA((CLOSE-TSMIN(LOW,9))/(TSMAX(HIGH,9)-TSMIN(LOW,9))*100,3,1),3,1)
    # Applies smoothing twice to the 9-day stochastic %K measure used in G28/G57 — a smoother, slower stochastic line.
    df = args[0]
    n = args[1]
    factor_name = args[2]
    df['G96_prepare_1'] = ((df['close'] - df['low'].rolling(9).min()) / ( df['high'].rolling(9).max() - df['low'].rolling(9).min())) * 100
    df['G96_prepare_2'] = df['G96_prepare_1'].ewm(alpha=1 / 3, adjust=False).mean()
    df['G96'] = df['G96_prepare_2'].ewm(alpha=1 / 3, adjust=False).mean()
    df[factor_name] = df['G96']
    df.drop(columns=['G96_prepare_1', 'G96_prepare_2', 'G96'], errors='ignore', inplace=True)

    return df
