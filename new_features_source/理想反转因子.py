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

fin_cols = []  # 财务因子列


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
    配置：('理想反转因子', is_sort_asc, n, arg)
    含义： 单笔成交金额 = 成交额 / 成交量, M_high = 过去N天内，单笔成交金额最大的50%交易日的总涨跌幅, M_low = 过去N天内，单笔成交金额最小的50%交易日的总涨跌幅
        理想反转因子 = M_high - M_low
    示例：'factor_list': [
                            ('理想反转因子', True, 20, 1),              # 理想反转因子_20
                        ]
    """
    # 从kwargs中提取因子列的名称
    col_name = kwargs['col_name']
    n = int(param)

    # 核心计算逻辑

    # df['单笔成交金额'] = df['成交额'] / df['成交量']
    # df['M_high'] = df['单笔成交金额'].rolling(n).apply(lambda x: df.loc[x.nlargest(int(n * 0.5)).index, '涨跌幅'].sum())
    # df['M_low'] = df['单笔成交金额'].rolling(n).apply(lambda x: df.loc[x.nsmallest(int(n * 0.5)).index, '涨跌幅'].sum())
    # df[f'理想反转因子_{n}'] = df['M_high'] - df['M_low']
    # del  df['单笔成交金额'], df['M_high'], df['M_low']

    # 改进后加速的方法，速度提升10倍以上
    def fast_reversal_factor(close_pct, trade_amount, n=20):
        result = np.zeros(len(close_pct))

        for i in range(n - 1, len(close_pct)):
            if i < n - 1:
                result[i] = np.nan
                continue

            # 获取窗口数据
            start_idx = i - n + 1
            window_amounts = trade_amount[start_idx:i + 1]
            window_returns = close_pct[start_idx:i + 1]

            # 使用np.partition快速找到中位数分割点
            k = int(n * 0.5)
            partitioned_indices = np.argpartition(window_amounts, k)

            # 大单部分（金额大的50%）
            big_order_indices = partitioned_indices[k:]
            big_order_returns = window_returns[big_order_indices]

            # 小单部分（金额小的50%）
            small_order_indices = partitioned_indices[:k]
            small_order_returns = window_returns[small_order_indices]

            result[i] = big_order_returns.sum() - small_order_returns.sum()

        return result

    # 使用方式
    df['单笔成交金额'] = df['成交额'] / df['成交量']
    df[f'理想反转因子_{n}'] = fast_reversal_factor(
        df['涨跌幅'].values,
        df['单笔成交金额'].values,
        n=n
    )
    factor_col = df[f'理想反转因子_{n}']
    del  df['单笔成交金额']
    # 创建包含指定因子的DataFrame
    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df
