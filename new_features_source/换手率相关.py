"""
邢不行｜策略分享会
选股策略框架𝓟𝓻𝓸

版权所有 ©️ 邢不行
微信: xbx1717

本代码仅供个人学习使用，未经授权不得复制、修改或用于商业用途。

Author: 邢不行
"""
import pandas as pd

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
    配置：('换手率相关', is_sort_asc, [method, n, m], arg)
    含义：全部缺省则为换手率本身，method是对换手率使用的相应算子，n为方法算子rolling天数，缺省值为1，m为在m天内取百分位排名
    示例：'factor_list': [
                            ('换手率相关', True, ['换手率', '', ''], 1),          # 换手率                            
                            ('换手率相关', True, ['ma', 5, ''], 1),              # 换手率_MA5
                            ('换手率相关', True, ['ema', 5, ''], 1),             # 换手率_EMA5
                            ('换手率相关', True, ['std', 5, ''], 1),             # 换手率_STD5
                            ('换手率相关', True, ['estd', 5, ''], 1),            # 换手率_ESTD5
                            ('换手率相关', True, ['min', 20, ''], 1),            # 换手率_MIN20   
                            ('换手率相关', True, ['max', 20, ''], 1),            # 换手率_MAX20 
                            ('换手率相关', True, ['diff', 5, ''], 1),            # 换手率_diff5
                            ('换手率相关', True, ['pct_change', 5, ''], 1),      # 换手率_pct5         
                            ('换手率相关', True, ['ma除std', 5, ''], 1),         # 换手率_MA5 / 换手率_STD5  
                            ('换手率相关', True, ['ma乘std', 5, ''], 1),         # 换手率_MA5 * 换手率_STD5      
                            ('换手率相关', True, ['换手率','',120], 1),           # 换手率_rank120                            
                            ('换手率相关', True, ['ma', 5, 120], 1),             # 换手率_MA5_rank120  
                            ('换手率相关', True, ['ema', 5, 120], 1),            # 换手率_EMA5_rank120  
                            ('换手率相关', True, ['std', 5, 120], 1),            # 换手率_STD5_rank120  
                            ('换手率相关', True, ['estd', 5, 120], 1),           # 换手率_ESTD5_rank120  
                            ('换手率相关', True, ['min', 20, 120], 1),           # 换手率_MIN20_rank120     
                            ('换手率相关', True, ['max', 20, 120], 1),           # 换手率_MAX20_rank120   
                            ('换手率相关', True, ['diff', 5, 120], 1),           # 换手率_diff5_rank120  
                            ('换手率相关', True, ['pct_change', 5, 120], 1),     # 换手率_pct5_rank120          
                            ('换手率相关', True, ['ma除std', 5, 120], 1),        # (换手率_MA5 / 换手率_STD5)_rank120    
                            ('换手率相关', True, ['ma乘std', 5, 120], 1),        # (换手率_MA5 * 换手率_STD5)_rank120                    
                        ],
    """

    # ======================== 参数处理 ===========================
    # 从kwargs中提取因子列的名称，这里使用'col_name'来标识因子列名称
    col_name = kwargs['col_name']

    # ======================== 计算基础指标 ========================
    base_col = '换手率'
    df[base_col] = df['成交额'] / df['流通市值']

    # ======================== 因子时序计算 ===========================

    # 参数规范化处理
    try:
        method, n, m = param
    except (TypeError, ValueError):
        raise ValueError("param参数必须是一个包含3个元素的序列(method, n, m)")

    # 验证参数有效性
    valid_methods = ['换手率', 'ma', 'ema', 'std', 'estd', 'min', 'max', 'diff', 'pct_change', 'ma除std', 'ma乘std']
    if method not in valid_methods:
        raise ValueError(f"无效的method参数: {method}. 有效值为: {valid_methods}")

    # 设置默认滚动窗口
    n = max(1, int(n)) if n else 1
    m = max(1, int(m)) if m else 0
    # 计算方法选择
    if method == '换手率':
       factor = df[base_col]
    elif method == 'ma':
        factor = df[base_col].rolling(n, min_periods=1).mean()
    elif method == 'ema':
        factor = df[base_col].ewm(span=n, adjust=False).mean()
    elif method == 'std':
        factor = df[base_col].rolling(n, min_periods=1).std()
    elif method == 'estd':
        factor = df[base_col].ewm(span=n, adjust=False).std()
    elif method == 'min':
        factor = df[base_col].rolling(n, min_periods=1).min()
    elif method == 'max':
        factor = df[base_col].rolling(n, min_periods=1).max()
    elif method == 'diff':
        factor = df[base_col].diff(n)
    elif method == 'pct_change':
        factor = df[base_col].pct_change(n)
    elif method == 'ma除std':
        mean = df[base_col].rolling(n, min_periods=1).mean()
        std = df[base_col].rolling(n, min_periods=1).std()
        factor = mean / std.replace(0, 1e-6)  # 避免除以0
    elif method == 'ma乘std':
        mean = df[base_col].rolling(n, min_periods=1).mean()
        std = df[base_col].rolling(n, min_periods=1).std()
        factor = mean * std
    else:
        factor = df[base_col]

    # 时序归一化处理
    if m >= 1:
        factor = factor.rolling(m, min_periods=1).rank(pct=True)

    df[col_name] = factor
    return df[[col_name]]
