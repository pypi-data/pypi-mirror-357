import pandas as pd


def process_dataframe(df: pd.DataFrame,
                      date_column: str = 'date') -> pd.DataFrame:
    """
    处理数据框架 - Bruce_li_pro 专用方法

    参数:
        df: 输入数据框架
        date_column: 日期列名

    返回:
        处理后的数据框架
    """
    # 1. 日期标准化
    if date_column in df.columns:
        df[date_column] = pd.to_datetime(df[date_column])

    # 2. 空值处理 (Bruce_li_pro 特有逻辑)
    df.fillna({
        'value': df['value'].median(),
        'category': 'unknown'
    }, inplace=True)

    # 3. 异常值过滤
    return df[(df['value'] >= df['value'].quantile(0.05)) &
              (df['value'] <= df['value'].quantile(0.95))]