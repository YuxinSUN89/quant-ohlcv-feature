#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
邢不行™️选股框架
Python股票量化投资课程

版权所有 ©️ 邢不行
微信: xbx8662

未经授权，不得复制、修改、或使用本代码的全部或部分内容。仅限个人学习用途，禁止商业用途。

Author: 邢不行
"""
import math

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
    配置：('G166', is_sort_asc, n, arg)
    含义：G166 = -20 * (20 - 1)^1.5 * SUM(CLOSE / DELAY(CLOSE, 1) - 1 - MEAN(CLOSE / DELAY(CLOSE, 1) - 1, 20), 20)/((20 - 1) * (20 - 2)(SUM((CLOSE / DELAY(CLOSE, 1), 20) ^ 2, 20)) ^ 1.5)
    示例：'factor_list': [
                            ('G166', True, '', 1),         # G166
                        ]
    """
    # 从额外参数中获取因子名称
    col_name = kwargs['col_name']
    # ========== 原始计算逻辑开始 ==========
    df['20天内平均涨跌幅'] = df['涨跌幅'].rolling(20).mean()
    df['G_166_cal_1'] = (df['涨跌幅'] - df['20天内平均涨跌幅']).rolling(20).sum()
    df['G_166_cal_2'] = (20 - 1) * (20 - 2) * (df['涨跌幅'] + 1).pow(2).rolling(20).sum().pow(1.5)
    df['G166'] = -20 * (math.pow(19, 1.5)) * (df['G_166_cal_1'] / df['G_166_cal_2'])
    del df['20天内平均涨跌幅'], df['G_166_cal_1'], df['G_166_cal_2']
    # ========== 原始计算逻辑结束 ==========
    # 创建因子列
    factor_col = df['G166']
    # 创建包含指定因子的DataFrame
    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)
    return factor_df
