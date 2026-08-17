"""
邢不行™️选股框架
Python股票量化投资课程

版权所有 ©️ 邢不行
微信: xbx8662

未经授权，不得复制、修改、或使用本代码的全部或部分内容。仅限个人学习用途，禁止商业用途。

Author: 邢不行
"""
import pandas as pd
import numpy as np
# 财务因子列：此列表用于存储财务因子相关的列名称  
fin_cols = []  # 财务因子列，配置后系统会自动加载对应的财务数据
def scale_01(_s, _n):
    _s = (pd.Series(_s) - pd.Series(_s).rolling(_n, min_periods=1).min()) / (
        1e-9 + pd.Series(_s).rolling(_n, min_periods=1).max() - pd.Series(_s).rolling(_n, min_periods=1).min()
    )
    return pd.Series(_s)

def add_factor(df: pd.DataFrame, param=None, **kwargs) -> pd.DataFrame:
    """
    

    工作流程：
    1. 根据提供的参数计算股票的因子值
    2. 将因子值添加到原始行情数据DataFrame中

    :param df: pd.DataFrame，包含单只股票的K线数据，必须包括市场数据（如收盘价等）
    :param param: 因子计算所需的参数，这里是滚动窗口期n
    :param kwargs: 其他关键字参数，包括：
        - col_name: 新计算的因子列名
        - fin_data: 财务数据字典
    :return: pd.DataFrame: 包含新计算的因子列，与输入的df具有相同的索引
    """
    # 从额外参数中获取因子名称
    col_name = kwargs['col_name']
    n = int(param)

    # ========== 原始计算逻辑开始 ==========

    rtn = df['收盘价_复权'].diff()
    up = np.where(rtn > 0, rtn, 0)
    dn = np.where(rtn < 0, rtn.abs(), 0)
    a = pd.Series(up).rolling(n, min_periods=1).sum()
    b = pd.Series(dn).rolling(n, min_periods=1).sum()
    a *= 1e3
    b *= 1e3
    rsi = a / (1e-9 + a + b)
    rsi_middle = rsi.rolling(n, min_periods=1).mean()
    rsi_upper = rsi_middle + 2 * rsi.rolling(n, min_periods=1).std()
    rsi_ma = rsi.rolling(int(n / 2), min_periods=1).mean()
    signal = rsi_ma - rsi_upper
    # ========== 原始计算逻辑结束 ==========

    # 创建因子列
    df[f'DzrsiUpperSignal_{n}'] = scale_01(signal, n)
    factor_col = df[f'DzrsiUpperSignal_{n}']

    # 清理中间列（如果有）


    # 创建包含指定因子的DataFrame
    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df
