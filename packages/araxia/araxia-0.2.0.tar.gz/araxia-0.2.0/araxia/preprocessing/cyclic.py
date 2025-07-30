import numpy as np
import pandas as pd

def create_dataset_with_cyclic_features(ds, target_col='sales', lag=5):
    """
    Create a dataset with cyclic features for time series forecasting.
    
    Parameters:
    - ds: DataFrame containing the time series data.
    - target_col: Name of the target column to predict.
    - lag: Number of lagged observations to include as features.
    
    Returns:
    - X: Features array with cyclic features and lagged values.
    - y: Target values array.
    """
    ds = ds.copy()
    ds['sale_date'] = pd.to_datetime(ds['sale_date'])
    ds['day_of_week'] = ds['sale_date'].dt.weekday
    ds['day_of_month'] = ds['sale_date'].dt.day
    ds['month'] = ds['sale_date'].dt.month
    ds['is_weekend'] = ds['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)

    ds['dow_sin'] = np.sin(2 * np.pi * ds['day_of_week'] / 7)
    ds['dow_cos'] = np.cos(2 * np.pi * ds['day_of_week'] / 7)
    ds['month_sin'] = np.sin(2 * np.pi * ds['month'] / 12)
    ds['month_cos'] = np.cos(2 * np.pi * ds['month'] / 12)

    X, y = [], []
    for i in range(lag, len(ds)):
        lagged = ds[target_col].values[i - lag:i].tolist()
        row = ds.iloc[i]
        features = lagged + [
            row['dow_sin'], row['dow_cos'],
            row['day_of_week'],
            row['day_of_month'],
            row['month_sin'], row['month_cos'],
            row['is_weekend']
        ]
        X.append(features)
        y.append(row[target_col])
    return np.array(X), np.array(y)
