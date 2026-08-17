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
fin_cols = ['B_total_equity_atoopc@xbx','B_goodwill@xbx']  # 财务因子列，配置后系统会自动加载对应的财务数据


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
    配置：('捡烟蒂因子N日分位数', is_sort_asc, param, arg)
    含义： 捡烟蒂因子N日分位数 = Rank(总市值 / (净资产 - 商誉),n)
    示例：'factor_list': [
                            ('捡烟蒂因子N日分位数', True, 250, 1),              # PB_不含商誉_250日分位数
                        ]
    """
    # ======================== 参数处理 ===========================
    # 从额外参数中获取因子名称
    col_name = kwargs['col_name']
    n = int(param)

    # 相关字段说明
    # - B_total_equity_atoopc@xbx:归属母公司所有者权益
    # - B_goodwill@xbx:商誉

    # ======================== 计算因子 ===========================
    df['净资产_不含商誉'] = df['B_total_equity_atoopc@xbx'] - df['B_goodwill@xbx'].fillna(0)

    # PB_不含商誉：市净率（不含商誉）= 总市值 / 净资产不含商誉
    df['PB_不含商誉'] = np.where(
        df['净资产_不含商誉'] > 0,
        df['总市值'] / df['净资产_不含商誉'],
        np.nan
    )
    # 处理极端异常值（PB > 100视为异常）
    df.loc[df['PB_不含商誉'] > 100, 'PB_不含商誉'] = np.nan
    # PB_不含商誉历史分位数：计算PB在过去250个交易日中的分位数
    df[f'PB_不含商誉_{n}日分位数'] = df['PB_不含商誉'].rolling(250).rank(pct=True)
    del df['净资产_不含商誉'], df['PB_不含商誉']

    df[col_name] = df[f'PB_不含商誉_{n}日分位数']

    return df[[col_name]]
