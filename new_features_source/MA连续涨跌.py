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
import math

# 财务因子列：此列表用于存储财务因子相关的列名称
# fin_cols = []  # 财务因子列，配置后系统会自动加载对应的财务数据


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
    配置：('MA连续涨跌', is_sort_asc, [n, weight], arg)
    含义： 对每个交易日，检查过去N天内是否 收盘价相对MA(n)发生过金叉/死叉；
        若发生过金叉且之后价格持续在均线上方，则计算从金叉到当前日的持续天数
        若发生过死叉且之后价格持续在均线下方，则计算从死叉到当前日的持续天数
        如果持续天数小于阈值（weight * n），则归零
        n,weight的缺省值分别为20和0.7
    示例：'factor_list': [
                            ('MA连续涨跌', True, '', 1),                # MA连续涨跌_20_0.7
                            ('MA连续涨跌', True, [10, 0.5], 1),         # MA连续涨跌_10_0.5
                        ]
    """

    # ======================== 参数处理 ===========================
    # 从kwargs中提取因子列的名称，这里使用'col_name'来标识因子列名称
    col_name = kwargs["col_name"]

    # ======================== 计算因子 ===========================
    # 我们这里的市值因子使用总市值的数值
    [n, weight] = [int(param[0]), param[1]] if param else [20, 0.7]
    threshold = math.ceil(weight * n)
    
    # 计算均线和价格位置
    df[f'ma{n}'] = df["收盘价"].rolling(n).mean()
    df[f"above_ma{n}"] = np.where(df["收盘价"] > df[f'ma{n}'], 1, -1)
    df[f"shifted_above_ma{n}"] = df[f"above_ma{n}"].shift(1)
    
    # 找出金叉和死叉点
    df['cross_up'] = ((df[f'above_ma{n}'] == 1) & (df[f'shifted_above_ma{n}'] == -1)).astype(int)
    df['cross_down'] = ((df[f'above_ma{n}'] == -1) & (df[f'shifted_above_ma{n}'] == 1)).astype(int)
    
    # 初始化结果数组
    result = np.zeros(len(df))
    
    # 优化版本 - 使用NumPy数组进行计算
    above_ma = df[f'above_ma{n}'].values
    cross_up = df['cross_up'].values
    cross_down = df['cross_down'].values
    
    # 初始化计数器数组
    up_counter = np.zeros(len(df))
    down_counter = np.zeros(len(df))
    
    # 遍历计算连续天数
    for i in range(1, len(df)):
        # 处理金叉后的连续上涨
        if above_ma[i] == 1:  # 当前价格在均线上方
            if cross_up[i] == 1:  # 如果是金叉点
                up_counter[i] = 1
            elif above_ma[i-1] == 1:  # 如果前一天也在均线上方
                up_counter[i] = up_counter[i-1] + 1
            # 如果前一天在均线下方但不是金叉点，保持为0
        else:
            up_counter[i] = 0  # 价格不在均线上方，重置计数器
        
        # 处理死叉后的连续下跌
        if above_ma[i] == -1:  # 当前价格在均线下方
            if cross_down[i] == 1:  # 如果是死叉点
                down_counter[i] = 1
            elif above_ma[i-1] == -1:  # 如果前一天也在均线下方
                down_counter[i] = down_counter[i-1] + 1
            # 如果前一天在均线上方但不是死叉点，保持为0
        else:
            down_counter[i] = 0  # 价格不在均线下方，重置计数器
    
    # 合并上升和下降计数器
    result = np.maximum(up_counter, down_counter)
    
    # 应用阈值过滤
    result = np.where(result < threshold, 0, result)
    
    # 将结果保存到DataFrame
    df[col_name] = result
    
    # 清理临时列
    df.drop([f'ma{n}', f'above_ma{n}', f'shifted_above_ma{n}', 'cross_up', 'cross_down'], axis=1, inplace=True)
    
    
    # 原始代码（已注释）
    '''
    df[f'ma{n}'] = df["收盘价"].rolling(n).mean()
    df[f"above_ma{n}"] = np.where(df["收盘价"] > df[f'ma{n}'], 1, -1)
    df[f"shifted_above_ma{n}"] = df[f"above_ma{n}"].shift(1)
    cross_up_points = df[(df[f'above_ma{n}'] == 1) & (df[f'shifted_above_ma{n}'] == -1)].index
    cross_down_points = df[(df[f'above_ma{n}'] == -1) & (df[f'shifted_above_ma{n}'] == 1)].index

    df['counter'] = 0
    for i in range(n, len(df)):
        current_index = df.index[i]
        previous_indices = df.index[i-n:i]
        up_overlap_indices = cross_up_points.intersection(previous_indices)
        if not up_overlap_indices.empty:
            closest_cross_up_id = up_overlap_indices[-1]
            if df.loc[closest_cross_up_id:current_index, f'above_ma{n}'].eq(1).all():
                df.at[current_index, 'counter'] = (current_index - closest_cross_up_id + 1)

        down_overlap_indices = cross_down_points.intersection(previous_indices)
        if not down_overlap_indices.empty:
            closest_cross_down_id = down_overlap_indices[-1]
            if df.loc[closest_cross_down_id:current_index, f'above_ma{n}'].eq(-1).all():
                df.at[current_index, 'counter'] = (current_index - closest_cross_down_id + 1)

    df['counter'] = np.where(df['counter'] < math.ceil(weight * n), 0, df['counter'])
    df[col_name] = df['counter']
    '''



    # 返回新计算的因子列以及因子聚合方式
    return df[[col_name]]
