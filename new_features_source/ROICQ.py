"""
邢不行™️选股框架
Python股票量化投资课程

版权所有 ©️ 邢不行
微信: xbx8662

未经授权，不得复制、修改、或使用本代码的全部或部分内容。仅限个人学习用途，禁止商业用途。

Author: 邢不行
"""
import pandas as pd

fin_cols = ['B_total_owner_equity@xbx' , 'B_st_borrow@xbx' , 'B_noncurrent_liab_due_in1y@xbx' , 'B_lt_loan@xbx' , 'B_bond_payable@xbx', 'R_np@xbx_单季', 'R_interest_fee@xbx_单季', 'R_income_tax_cost@xbx_单季',
            'R_income_tax_cost@xbx_单季', 'R_total_profit@xbx_单季']  # 财务因子列


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
    配置：('ROICQ', is_sort_asc, n, arg)
    含义：资本投入 = 股东权益 + 短期借款 + 一年内到期的非流动负债 + 长期借款 + 应付债券, 税前息前利润_单季 = 净利润_单季 + 利息费用_单季 + 所得税费用_单季
        实际税率_单季 = 所得税费用_单季 / 利润总额_单季
        ROICQ = 税前息前利润_单季 * (1 - 实际税率_单季) / 资本投入
    示例：'factor_list': [
                            ('ROICQ', True, '', 1),         # ROICQ
                        ]
    """
    # 从kwargs中提取因子列的名称
    col_name = kwargs['col_name']

    # 核心计算逻辑
    df['资本投入'] = df['B_total_owner_equity@xbx'] + df['B_st_borrow@xbx'] + df['B_noncurrent_liab_due_in1y@xbx'] + df['B_lt_loan@xbx'] + df['B_bond_payable@xbx']
    df['EBIT单季_税'] = df['R_np@xbx_单季'] + df['R_interest_fee@xbx_单季'].fillna(0) + df['R_income_tax_cost@xbx_单季']
    df['T_单季'] = df['R_income_tax_cost@xbx_单季'] / df['R_total_profit@xbx_单季']
    df['ROICQ'] = df['EBIT单季_税'] * (1 - df['T_单季']) / df['资本投入']
    factor_col = df['ROICQ']
    del  df['资本投入'], df['EBIT单季_税'], df['T_单季']
    # 创建包含指定因子的DataFrame
    factor_df = pd.DataFrame({col_name: factor_col}, index=df.index)

    return factor_df
