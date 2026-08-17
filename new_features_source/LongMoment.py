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
    配置：('LongMoment', is_sort_asc, n, arg)
    含义：LongMoment = 基于振幅筛选的低波动股票在N日窗口内的涨跌幅动量因子
    示例：'factor_list': [
                            ('LongMoment', True, 20, 1),         # LongMoment_20
                        ]
    """
    # 从额外参数中获取因子名称
    col_name = kwargs['col_name']
    n = int(param)

    # ========== 原始计算逻辑开始 ==========


    # ========== 原始计算逻辑结束 ==========

    # 创建因子列
    df['涨跌幅'] = df['收盘价_复权'].pct_change(n)
    # 计算窗口20-180的切割动量与反转因子
    df['振幅'] = (df['最高价_复权'] / df['最低价_复权']) - 1
    # 先把需要滚动的两列数据变成array
    np_tmp = df[['振幅', '涨跌幅']].values
    # 计算因子
    df[f'LongMoment_{n}'] = df['涨跌幅'].rolling(n * 10).apply(range_plus, args=(np_tmp, n * 10, 0.7), raw=False)
    factor_col = df[f'LongMoment_{n}']
    # 清理中间列（如果有）
    del df['振幅'], df['涨跌幅']

    # 创建包含指定因子的DataFrame
    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df

def range_plus(x, np_tmp, rolling_window, lam):
    # 计算滚动到的index
    li = x.index.to_list()
    # 从整块array中截取对应的index的array块
    np_tmp2 = np_tmp[li, :]
    # 按照振幅排序
    np_tmp2 = np_tmp2[np.argsort(np_tmp2[:, 0])]
    # 计算需要切分的个数
    t = int(rolling_window * lam)
    # 计算低价涨跌幅因子
    np_tmp2 = np_tmp2[:t, :]
    s = np_tmp2[:, 1].sum()
    return s