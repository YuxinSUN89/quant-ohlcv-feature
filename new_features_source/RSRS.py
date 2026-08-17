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
from scipy import stats

# 财务因子列：此列表用于存储财务因子相关的列名称
fin_cols = []  # 财务因子列，配置后系统会自动加载对应的财务数据


def add_factor(df: pd.DataFrame, param=None, **kwargs) -> (pd.DataFrame, dict):
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
    配置：('RSRS', is_sort_asc, [n, m], arg)
    含义：beta = n日内股价线性回归斜率
        RSRS = (beta - MA(beta, m)) / STD(beta, m) * 收盘价 / 开盘价, n和m的缺省值为20和20
    示例：'factor_list': [
                            ('RSRS', True, '', 1),              # RSRS_20_20
                            ('RSRS', True, [30, 20], 1),         # RSRS_30_20
                        ]
    """

    # ======================== 参数处理 ===========================
    # 从kwargs中提取因子列的名称，这里使用'col_name'来标识因子列名称
    col_name = kwargs['col_name']
    
    # ======================== 计算因子 ===========================
    # 我们这里的市值因子使用流通市值的数值
    betas = []
    [n, m] = [int(param[0]), int(param[1])] if param else [20, 20]
    # threshold = 0.7

    # 1. 使用线性代数方法批量计算回归斜率
    def vectorized_beta_calculation(high, low, window):
        length = len(high)
        betas = np.full(length, np.nan)

        for i in range(window - 1, length):
            x = low[i - window + 1:i + 1]
            y = high[i - window + 1:i + 1]

            # 向量化计算回归参数
            x_mean = np.mean(x)
            y_mean = np.mean(y)
            numerator = np.sum((x - x_mean) * (y - y_mean))
            denominator = np.sum((x - x_mean) ** 2)

            if denominator != 0:
                betas[i] = numerator / denominator

        return betas

    # 2. 计算beta值
    high_prices = df['最高价'].values
    low_prices = df['最低价'].values
    df['beta'] = vectorized_beta_calculation(high_prices, low_prices, n)

    # 替换原有计算方法，可以大幅度提高计算速度
    # for i in range(len(df)):
    #     if i < n -1:
    #         betas.append(np.nan)
    #         continue
    #     window = df.iloc[i - n+1:i+1]
    #     x = window['最低价'].values
    #     y = window['最高价'].values
    #
    #     # 手动计算回归斜率
    #     x_mean = np.mean(x)
    #     y_mean = np.mean(y)
    #     numerator = np.sum((x - x_mean) * (y - y_mean))
    #     denominator = np.sum((x - x_mean) ** 2)
    #     beta = numerator / denominator if denominator !=0 else 0
    #     betas.append(beta)
    #
    # df['beta'] = betas
    
    # 标准化z-score
    df['beta_mean'] = df['beta'].rolling(m).mean()
    df['beta_std'] = df['beta'].rolling(m).std()
    df['Z'] = (df['beta'] - df['beta_mean']) / df['beta_std']
    
    # 右偏修正
    df['修正因子']= df['收盘价'] / df['开盘价']
    df['RSRS'] = df['Z'] * df['修正因子']
    df[col_name] = df['RSRS']

    # 返回新计算的因子列以及因子聚合方式
    return df[[col_name]]
