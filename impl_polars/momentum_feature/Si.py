import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Si indicator
    """
    A=ABS(HIGH-REF(CLOSE,1))
    B=ABS(LOW-REF(CLOSE,1))
    C=ABS(HIGH-REF(LOW,1))
    D=ABS(REF(CLOSE,1)-REF(OPEN,1))
    N=20
    K=MAX(A,B)
    M=MAX(HIGH-LOW,N)
    R1=A+0.5*B+0.25*D
    R2=B+0.5*A+0.25*D
    R3=C+0.25*D
    R4=IF((A>=B) & (A>=C),R1,R2)
    R=IF((C>=A) & (C>=B),R3,R4)
    Si=50*(CLOSE-REF(CLOSE,1)+(REF(CLOSE,1)-REF(OPEN,1))+
    0.5*(CLOSE-OPEN))/R*K/M
    Si uses a weighted average of price changes (two-day close difference, yesterday's
    close-open difference, today's close-open difference) to reflect price movement.
    Buy/sell signals are generated when Si crosses above/below 0.
    """
    df = df.with_columns(pl.Series("A", abs(df["high"] - df["close"].shift(1))))
    df = df.with_columns(pl.Series("B", abs(df["low"] - df["close"].shift(1))))
    df = df.with_columns(pl.Series("C", abs(df["high"] - df["low"].shift(1))))
    df = df.with_columns(pl.Series("D", abs(df["close"].shift(1) - df["open"].shift(1))))
    df = df.with_columns(K=pl.max_horizontal([pl.col("A"), pl.col("B")]))
    df = df.with_columns(pl.Series("M", (df["high"] - df["low"]).rolling_max(n, min_samples=config.min_periods)))
    df = df.with_columns(pl.Series("R1", df["A"] + 0.5 * df["B"] + 0.25 * df["D"]))
    df = df.with_columns(pl.Series("R2", df["B"] + 0.5 * df["A"] + 0.25 * df["D"]))
    df = df.with_columns(pl.Series("R3", df["C"] + 0.25 * df["D"]))
    df = df.with_columns(
        pl.Series("R4", np.where((df["A"] >= df["B"]) & (df["A"] >= df["C"]), df["R1"], df["R2"])).fill_nan(None)
    )
    df = df.with_columns(
        pl.Series("R", np.where((df["C"] >= df["A"]) & (df["C"] >= df["B"]), df["R3"], df["R4"])).fill_nan(None)
    )
    df = df.with_columns(
        pl.Series(
            factor_name,
            50
            * (
                df["close"]
                - df["close"].shift(1)
                + (df["close"].shift(1) - df["open"].shift(1))
                + 0.5 * (df["close"] - df["open"])
            )
            / (df["R"] + config.eps)
            * df["K"]
            / (df["M"] + config.eps),
        )
    )

    df = df.drop("A")
    df = df.drop("B")
    df = df.drop("C")
    df = df.drop("D")
    df = df.drop("K")
    df = df.drop("M")
    df = df.drop("R1")
    df = df.drop("R2")
    df = df.drop("R3")
    df = df.drop("R4")
    df = df.drop("R")
    # df = df.drop('Si')

    return df
