
import numpy as np
import pandas as pd

def create_dataset_with_onehot_dow(df, target_col='sales', lag=5):
    df = df.copy()
    df['sale_date'] = pd.to_datetime(df['sale_date'])
    df['day_of_week'] = df['sale_date'].dt.weekday
    df['day_of_month'] = df['sale_date'].dt.day
    df['month'] = df['sale_date'].dt.month
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)

    X, y = [], []
    for i in range(lag, len(df)):
        lagged = df[target_col].values[i - lag:i].tolist()
        row = df.iloc[i]
        onehot_dow = [1 if j == row['day_of_week'] else 0 for j in range(7)]
        features = lagged + onehot_dow + [
            row['day_of_month'],
            row['month'],
            row['is_weekend']
        ]
        X.append(features)
        y.append(row[target_col])
    return np.array(X), np.array(y)