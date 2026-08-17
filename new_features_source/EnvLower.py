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

def add_factor(df: pd.DataFrame, param=None, **kwargs) -> pd.DataFrame:
    """
    计算并将新的因子列添加到股票行情数据中，并返回包含计算因子的DataFrame及其聚合方式。

    工作流程：
    1. 根据提供的参数计算股票的因子值。
    2. 将因子值添加到原始行情数据DataFrame中。

    :param df: pd.DataFrame，包含单只股票的K线数据，必须包括市场数据（如收盘价等）。
    :param param: 因子计算所需的参数，格式和含义根据因子类型的不同而有所不同。
    :param kwargs: 其他关键字参数，包括：
        - col_name: 新计算的因子列名。
        - fin_data: 财务数据字典，格式为 {'财务数据': fin_df, '原始财务数据': raw_fin_df}，其中fin_df为处理后的财务数据，raw_fin_df为原始数据，后者可用于某些因子的自定义计算。
        - 其他参数：根据具体需求传入的其他因子参数。
    :return:
        - pd.DataFrame: 包含新计算的因子列，与输入的df具有相同的索引。

    注意事项：
    - 如果因子的计算涉及财务数据，可以通过`fin_data`参数提供相关数据。
    """
    """    
    ----->>>  配置方法  <<<-----
    配置：('EnvLower', is_sort_asc, n, arg)
    含义：EnvLower = scale01((1-0.15) * MA(n))  ENV指标是由移动平均线上下平移一定的幅度 (百分比,这里是15%)所得。 n缺省值25
    示例：'factor_list': [
                            ('EnvLower', True, '', 1),         # EnvLower_25
                            ('EnvLower', True, 10, 1),         # EnvLower_10
                        ]
    """
    # 从额外参数中获取因子名称
    col_name = kwargs['col_name']
    n = int(param) if param else 25

    # ========== 原始计算逻辑开始 ==========
    lower = (1 - 0.05) * df['收盘价_复权'].rolling(n, min_periods=1).mean()
    signal = lower
    # ========== 原始计算逻辑结束 ==========

    # 创建因子列
    df[f'EnvLower_{n}'] = scale_01(signal, n)
    factor_col = df[f'EnvLower_{n}']

    # 清理中间列（如果有）


    # 创建包含指定因子的DataFrame
    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df

def scale_01(_s, _n):
    _s = (pd.Series(_s) - pd.Series(_s).rolling(_n, min_periods=1).min()) / (
        1e-9 + pd.Series(_s).rolling(_n, min_periods=1).max() - pd.Series(_s).rolling(_n, min_periods=1).min()
    )
    return pd.Series(_s)
