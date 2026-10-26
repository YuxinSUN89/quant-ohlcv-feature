"""
BidaskSpread — EDGE bid-ask spread estimator from OHLC prices
=============================================================

Source
------
Ardia, D., Guidotti, E., & Kroencke, T. A. (2024). "Efficient estimation of
bid-ask spreads from open, high, low, and close prices".
Journal of Financial Economics, 161, 103916.
https://doi.org/10.1016/j.jfineco.2024.103916
Reference implementation: https://github.com/eguidotti/bidask

What it measures
----------------
The effective bid-ask spread, i.e. the round-trip cost of trading relative to
the unobserved fundamental price, S = 2 * D * (P - P~) / P~  (paper Eq. 1),
estimated from bar prices only, with no trade or quote data.
Output is a fraction: 0.01 = 1% spread. Higher values mean the market is less
liquid and costs more to trade in.

Idea
----
Observed log-prices are the fundamental price plus a bid-ask bounce,
p = p~ + Z with Z = +/- S/2 (Eq. 4). Under three mild assumptions
(fundamental returns serially uncorrelated, uncorrelated with the bounce, and
bounces uncorrelated with zero mean), the bounce makes consecutive returns
negatively autocorrelated, and the size of that covariance identifies S^2.

Unlike Roll (1984), Corwin-Schultz (2012) and Abdi-Ranaldo (2017), EDGE does
not assume prices are observed continuously. When few trades happen per bar,
the open or close often coincides with the high or low. EDGE corrects for this
analytically, so it stays unbiased for illiquid assets and for intraday bars
(minute / hourly crypto data included, paper Section 6.3).

Notation (log-prices):  o, h, l, c = open, high, low, close
                        eta = (h + l) / 2   mid-range price
                        suffix 1 = previous bar (t-1)

Indicator  tau_t = 0 if h_t == l_t == c_{t-1} (flat / no-trade bar), else 1  (Eq. 7)

Four Discrete Generalized Estimators (Table 1):
    OHL  : S_o^2 = pi_o * E[(eta_t - o_t)(o_t - eta_{t-1})]
    OHLC : S_o^2 = pi_o * E[(eta_t - o_t)(o_t - c_{t-1})]
    CHL  : S_c^2 = pi_c * E[(eta_t - c_{t-1})(c_{t-1} - eta_{t-1})]
    CHLO : S_c^2 = pi_c * E[(o_t - c_{t-1})(c_{t-1} - eta_{t-1})]
    pi_o = -8 / (P[o_t != h_t, tau=1] + P[o_t != l_t, tau=1])
    pi_c = -8 / (P[c_{t-1} != h_{t-1}, tau=1] + P[c_{t-1} != l_{t-1}, tau=1])
Returns are de-meaned as r - tau * E[r] / E[tau]  (Eq. 9).

OHL/CHL have low variance when the spread is large relative to volatility;
OHLC/CHLO have low variance when it is small. EDGE pairs them into two moment
conditions (Eq. 24)
    x1 = pi_o/2 * OHL-term  + pi_c/2 * CHL-term
    x2 = pi_o/2 * OHLC-term + pi_c/2 * CHLO-term
and combines them with inverse-variance (GMM, diagonal weights) (Eqs. 23, 25):
    S^2 = w1 * E[x1] + w2 * E[x2],  w1 = Var[x2] / (Var[x1] + Var[x2]),  w2 = 1 - w1
If Var[x1] + Var[x2] <= 0, an equal-weighted average is used instead.

Negative estimates
------------------
In small samples S^2 can come out negative. The paper reports max(0, S^2)
(Eq. 26). This implementation instead returns sqrt(|S^2|), the alternative
suggested in Section 3.2: it avoids a pile-up of zeros, which helps a
continuous ML feature. Pass sign=True to edge_rolling to get
sign(S^2) * sqrt(|S^2|) and recover the paper's convention with .clip(lower=0).

Factor definition (signal)
--------------------------
    bidask_t = EDGE over a rolling window of 1000 bars ending at t
    result   = MA(bidask, N)        (min_periods=1)
The long fixed window keeps estimation noise low (standard error falls with
sample size, Section 6.2); N only controls the extra smoothing.

Practical notes
---------------
- Needs only open/high/low/close (column names are case-insensitive). Volume is unused.
- Prices must be strictly positive (log-prices are used).
- The first ~1000 bars are NaN while the window fills. The result is also NaN
  when there are fewer than 2 non-flat bars in the window, or when the
  open/close always equals the high/low (the spread is undefined there).
- Noisier on daily bars for very liquid assets, where the spread is small
  relative to volatility. Intraday bars improve the estimate substantially.
"""

import pandas as pd
import numpy as np


def edge_rolling(df: pd.DataFrame, window: int, sign: bool = False, **kwargs) -> pd.Series:
    """
    Rolling Estimates of Bid-Ask Spreads from Open, High, Low, and Close Prices

    Implements a rolling window calculation of the efficient estimator of bid-ask spreads
    from open, high, low, and close prices described in Ardia, Guidotti, & Kroencke (JFE, 2024):
    https://doi.org/10.1016/j.jfineco.2024.103916

    Parameters
    ----------
    - `df` : pd.DataFrame
        DataFrame with columns 'open', 'high', 'low', 'close' (case-insensitive).
    - `window` : int, timedelta, str, offset, or BaseIndexer subclass
        Size of the moving window. For more information about this parameter, see
        https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html
    - `sign` : bool, default False
        If False, return sqrt(|S^2|). If True, return sign(S^2) * sqrt(|S^2|), so
        negative raw estimates are visible (clip at 0 for the paper's Eq. 26).
    - `kwargs` : dict, optional
        Additional keyword arguments to pass to the pandas rolling function.
        For more information about the rolling parameters, see
        https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rolling.html

    Returns
    -------
    pd.Series
        A pandas Series of rolling spread estimates. A value of 0.01 corresponds to a spread of 1%.
    """
    # compute log-prices
    df = df.rename(columns=str.lower, inplace=False)
    o = np.log(df['open'])
    h = np.log(df['high'])
    l = np.log(df['low'])
    c = np.log(df['close'])
    m = (h + l) / 2.

    # shift log-prices by one period
    h1 = h.shift(1)
    l1 = l.shift(1)
    c1 = c.shift(1)
    m1 = m.shift(1)

    # compute log-returns
    r1 = m - o      # eta_t - o_t       (open-to-mid)
    r2 = o - m1     # o_t - eta_{t-1}   (mid-to-open)
    r3 = m - c1     # eta_t - c_{t-1}   (close-to-mid)
    r4 = c1 - m1    # c_{t-1} - eta_{t-1} (mid-to-close)
    r5 = o - c1     # o_t - c_{t-1}     (close-to-open)

    # compute indicator variables
    # tau: 0 on flat bars (h == l == previous close), Eq. (7)
    # po1/po2 (pc1/pc2): open (previous close) differs from high/low, used for pi_o (pi_c)
    tau = np.where(np.isnan(h) | np.isnan(l) | np.isnan(c1), np.nan, (h != l) | (l != c1))
    po1 = tau * np.where(np.isnan(o) | np.isnan(h), np.nan, o != h)
    po2 = tau * np.where(np.isnan(o) | np.isnan(l), np.nan, o != l)
    pc1 = tau * np.where(np.isnan(c1) | np.isnan(h1), np.nan, c1 != h1)
    pc2 = tau * np.where(np.isnan(c1) | np.isnan(l1), np.nan, c1 != l1)

    # compute base products for rolling means
    r12 = r1 * r2   # OHL term
    r15 = r1 * r5   # OHLC term
    r34 = r3 * r4   # CHL term
    r45 = r4 * r5   # CHLO term
    tr1 = tau * r1
    tr2 = tau * r2
    tr4 = tau * r4
    tr5 = tau * r5

    # set up data frame for rolling means: every first/second moment needed for
    # the de-meaned expectations and variances of x1, x2 is a rolling mean of one column
    x = pd.DataFrame({
        1: r12,
        2: r34,
        3: r15,
        4: r45,
        5: tau,
        6: r1,
        7: tr2,
        8: r3,
        9: tr4,
        10: r5,
        11: r12 ** 2,
        12: r34 ** 2,
        13: r15 ** 2,
        14: r45 ** 2,
        15: r12 * r34,
        16: r15 * r45,
        17: tr2 * r2,
        18: tr4 * r4,
        19: tr5 * r5,
        20: tr2 * r12,
        21: tr4 * r34,
        22: tr5 * r15,
        23: tr4 * r45,
        24: tr4 * r12,
        25: tr2 * r34,
        26: tr2 * r4,
        27: tr1 * r45,
        28: tr5 * r45,
        29: tr4 * r5,
        30: tr5,
        31: po1,
        32: po2,
        33: pc1,
        34: pc2
    }, index=df.index)

    # mask the first observation and decrement window and min_periods by 1 before
    # computing rolling means to account for lagged prices
    x.iloc[0] = np.nan
    if isinstance(window, (int, np.integer)):
        window = max(0, window - 1)
    if 'min_periods' in kwargs and isinstance(kwargs['min_periods'], (int, np.integer)):
        kwargs['min_periods'] = max(0, kwargs['min_periods'] - 1)

    # compute rolling means
    m = x.rolling(window=window, **kwargs).mean()

    # compute probabilities
    pt = m[5]
    po = m[31] + m[32]
    pc = m[33] + m[34]

    # set to missing if there are less than two periods with tau=1
    # or po or pc is zero
    nt = x[5].rolling(window=window, **kwargs).sum()
    m[(nt < 2) | (po == 0) | (pc == 0)] = np.nan

    # compute input vectors
    # a1 = pi_o / 2, a2 = pi_c / 2; a3..a6 = E[r] / E[tau] de-meaning factors, Eq. (9)
    a1 = -4. / po
    a2 = -4. / pc
    a3 = m[6] / pt
    a4 = m[9] / pt
    a5 = m[8] / pt
    a6 = m[10] / pt
    a12 = 2 * a1 * a2
    a11 = a1 ** 2
    a22 = a2 ** 2
    a33 = a3 ** 2
    a55 = a5 ** 2
    a66 = a6 ** 2

    # compute expectations: e1 = E[x1] (OHL + CHL), e2 = E[x2] (OHLC + CHLO), Eq. (24)
    e1 = a1 * (m[1] - a3 * m[7]) + a2 * (m[2] - a4 * m[8])
    e2 = a1 * (m[3] - a3 * m[30]) + a2 * (m[4] - a4 * m[10])

    # compute variances: v1 = Var[x1], v2 = Var[x2]
    v1 = - e1 ** 2 + (
            a11 * (m[11] - 2 * a3 * m[20] + a33 * m[17]) +
            a22 * (m[12] - 2 * a5 * m[21] + a55 * m[18]) +
            a12 * (m[15] - a3 * m[25] - a5 * m[24] + a3 * a5 * m[26])
    )
    v2 = - e2 ** 2 + (
            a11 * (m[13] - 2 * a3 * m[22] + a33 * m[19]) +
            a22 * (m[14] - 2 * a6 * m[23] + a66 * m[18]) +
            a12 * (m[16] - a3 * m[28] - a6 * m[27] + a3 * a6 * m[29])
    )

    # compute square spread by using a (equally) weighted
    # average if the total variance is (not) positive, Eqs. (23), (25)
    vt = v1 + v2
    s2 = pd.Series.where(
        cond=vt > 0,
        self=(v2 * e1 + v1 * e2) / vt,
        other=(e1 + e2) / 2.
    )

    # compute signed root
    s = np.sqrt(np.abs(s2))
    if sign:
        s *= np.sign(s2)

    # return the spread
    return s


def signal(*args):
    # BidaskSpread indicator (EDGE effective bid-ask spread, Ardia-Guidotti-Kroencke JFE 2024)
    # Formula: BIDASK = EDGE(OPEN, HIGH, LOW, CLOSE) over a rolling 1000-bar window
    #          result = MA(BIDASK, N)
    # Estimates the effective bid-ask spread from the negative serial covariance that the
    # bid-ask bounce induces in open/high/low/close returns, corrected for discretely observed prices.
    # Output is a fraction (0.01 = 1%). Higher values mean higher transaction costs and lower liquidity.
    df = args[0]
    n = args[1]
    factor_name = args[2]

    # Compute rolling bid-ask spread estimates from open/high/low/close.
    spread_df = edge_rolling(df, window=1000).to_frame(name='bidask')
    df = pd.concat([df, spread_df], axis=1)

    # Smooth the spread estimate over the requested window.
    df[factor_name] = df['bidask'].rolling(window=n, min_periods=1).mean()

    del df['bidask']

    return df