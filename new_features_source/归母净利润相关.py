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
fin_cols = ['R_np_atoopc@xbx_单季', 'R_np_atoopc@xbx_ttm', 'R_np_atoopc@xbx_ttm同比', 'R_np_atoopc@xbx_累计同比', 'R_np_atoopc@xbx_单季同比',  'R_np_atoopc@xbx_单季环比']  # 财务因子列，配置后系统会自动加载对应的财务数据


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
    配置：('归母净利润相关', is_sort_asc, param, arg)
    含义： 各类归母净利润相关的因子
    示例：'factor_list': [
                            ('归母净利润相关', True, '全年', 1),              # 归母净利润_全年
                            ('归母净利润相关', True, '全年同比', 1),           # 归母净利润_全年同比
                            ('归母净利润相关', True, '累计同比', 1),           # 归母净利润_累计同比
                            ('归母净利润相关', True, '单季', 1),              # 归母净利润_单季
                            ('归母净利润相关', True, '单季同比', 1),           # 归母净利润_单季同比     
                            ('归母净利润相关', True, '单季环比', 1),           # 归母净利润_单季环比                   
                            ('归母净利润相关', True, '全年同比季度增加', 1),     # 归母净利润_全年同比增速季度增加
                            ('归母净利润相关', True, '累计同比季度增加', 1),     # 归母净利润_累计同比增速季度增加
                            ('归母净利润相关', True, '单季同比季度增加', 1),     # 归母净利润_单季同比增速季度增加
                            ('归母净利润相关', True, '单季环比季度增加', 1),     # 归母净利润_单季环比增速季度增加     
                        ]
    """
    # ======================== 参数处理 ===========================
    # 从kwargs中提取因子列的名称，这里使用'col_name'来标识因子列名称
    col_name = kwargs['col_name']

    # 归母净利润相关字段说明
    # - R_np_atoopc@xbx_ttm:归母净利润ttm
    # - R_np_atoopc@xbx_ttm同比:归母净利润ttm同比
    # - R_np_atoopc@xbx_累计同比:归母净利润累计同比
    # - R_np_atoopc@xbx_单季:归母净利润单季度
    # - R_np_atoopc@xbx_单季同比:归母净利润单季度同比
    # - R_np_atoopc@xbx_单季环比:归母净利润单季度环比
    param1_cols = {
        '全年': 'R_np_atoopc@xbx_ttm',
        '全年同比': 'R_np_atoopc@xbx_ttm同比',
        '累计同比': 'R_np_atoopc@xbx_累计同比',
        '单季': 'R_np_atoopc@xbx_单季',
        '单季同比': 'R_np_atoopc@xbx_单季同比',
        '单季环比': 'R_np_atoopc@xbx_单季环比',
    }
    param2_cols = {
        '全年同比季度增加': 'R_np_atoopc@xbx_ttm同比',
        '累计同比季度增加': 'R_np_atoopc@xbx_累计同比',
        '单季同比季度增加': 'R_np_atoopc@xbx_单季同比',
        '单季环比季度增加': 'R_np_atoopc@xbx_单季环比',
    }
    param_cols = param1_cols | param2_cols

    # 根据param选择相应的归母净利润字段
    if param not in param_cols:
        factor_name = __file__.replace('\\', '/').split('/')[-1].replace('.py', '')
        raise ValueError(f"{factor_name} 因子不支持的参数值：{param}")
    else:
        param_col = param_cols[param]

    # ======================== 计算因子 ===========================
    # 如果不需要计算增速
    if param in param1_cols:
        df[col_name] = df[param_col]
    # 如果需要计算增速
    else:
        # 计算上一个不一样值的差值，作为季度增加
        df[f'{param_col}_值变化'] = df.groupby('股票代码')[f'{param_col}'].transform(lambda x: x.diff() != 0)
        df[f'临时_{param_col}_季度增加'] = np.nan
        mask = df[f'{param_col}_值变化']  # 只在同比值变化的日期计算
        df.loc[mask, f'临时_{param_col}_季度增加'] = df.loc[mask, f'{param_col}'].diff()
        df[f'{param_col}_季度增加'] = df.groupby('股票代码')[f'临时_{param_col}_季度增加'].transform('ffill')
        df[col_name] = df[f'{param_col}_季度增加']

        del df[f'{param_col}_值变化'], df[f'临时_{param_col}_季度增加'], df[f'{param_col}_季度增加']

    return df[[col_name]]
