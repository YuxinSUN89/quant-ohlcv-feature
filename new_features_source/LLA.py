import pandas as pd
import numpy as np

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
    配置：('LLA', is_sort_asc, n, arg)
    含义：LLA同时描述股价低位、波动收缩、成交量萎缩、主力吸筹四个现象，彼此相乘，满足的条件越多高因子值, n的缺省值为13
    示例：'factor_list': [
                            ('LLA', True, '', 1),         # LLA_13
                            ('LLA', True, 30, 1),         # LLA_30
                        ]
    """

    # ======================== 参数处理 ===========================
    col_name = kwargs['col_name']
    
    # 使用单一参数n
    n = int(param) if param else 13
    
    # ======================== 计算因子 ===========================
    
    # 1. 低位识别组件
    price_high = df['最高价'].rolling(window=n).max()
    price_low = df['最低价'].rolling(window=n).min()
    price_range = price_high - price_low
    price_range = price_range.replace(0, np.nan).fillna(df['收盘价'] * 0.001)
    relative_position = (df['收盘价'] - price_low) / price_range
    
    low_position = np.clip(1 - relative_position * 2.5, 0, 1)
    
    # 2. 横盘识别组件
    tr = pd.DataFrame({
        'hl': df['最高价'] - df['最低价'],
        'hc': abs(df['最高价'] - df['收盘价'].shift(1)),
        'lc': abs(df['最低价'] - df['收盘价'].shift(1))
    }).max(axis=1)
    
    atr = tr.rolling(window=n).mean()
    atr_ratio = atr / df['收盘价']
    
    hist_atr_ratio = atr_ratio.rolling(window=n*2).mean()
    volatility_decline = np.clip(1 - (atr_ratio / hist_atr_ratio), 0, 1)
    
    # 3. 成交量萎缩组件
    volume_ma = df['成交额'].rolling(window=n).mean()
    volume_ratio = df['成交额'] / volume_ma
    
    volume_decline = np.clip(1 - volume_ratio, 0, 0.8)
    
    # 4. 主力资金进入组件
    daily_return = df['收盘价'].pct_change()
    
    small_positive_volume = ((daily_return > 0) & (volume_ratio < 1)).astype(int)
    large_positive_volume = ((daily_return > 0) & (volume_ratio >= 1)).astype(int)
    
    small_pos_ratio = small_positive_volume.rolling(window=n).sum() / 5
    
    # 5. 价升量缩特征
    price_up_volume_down = ((daily_return.shift(1) > 0) & 
                            (volume_ratio < 0.9) & 
                            (daily_return > -0.01)).astype(float) * 2
    
    price_up_volume_down = price_up_volume_down.rolling(window=n).sum() / 10
    
    df[col_name] = (low_position * 
                    volatility_decline * 
                    (1 + volume_decline) * 
                    (1 + small_pos_ratio + price_up_volume_down))
    
    df[col_name] = df[col_name].replace([np.inf, -np.inf], np.nan)
    df[col_name] = df[col_name].fillna(0)
    df[col_name] = np.log1p(df[col_name])
        

    
    return df[[col_name]]
