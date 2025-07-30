import numpy as np
import pandas as pd

def create_lagged_dataset(ds, date_col='sale_date', target_col='sales', lag=5):
    """Create a lagged dataset for time series forecasting.
    
    Parameters:
        ds (pd.DataFrame): DataFrame containing the time series data.
        date_col (str): The name of the date column in the DataFrame.
        target_col (str): The name of the target column to forecast.
        lag (int): The number of lagged observations to include.
        
    Returns:
        X (np.ndarray): Array of lagged features.
        y (np.ndarray): Array of target values."""
    X, y = [], []

    ds[date_col] = pd.to_datetime(ds[date_col])
    ds = ds.sort_values(date_col)

    ds['day_of_week'] = ds[date_col].dt.weekday
    ds['is_weekend'] = ds['day_of_week'].isin([5, 6])
    ds['day_of_month'] = ds[date_col].dt.day
    ds['month'] = ds[date_col].dt.month    


    for i in range(lag, len(ds)):
        lagged_values = ds[date_col].values[i - lag:i].tolist()
        row = ds.iloc[i]
        features = lagged_values + [
            row['day_of_week'],
            row['day_of_month'],
            row['month'],
            row['is_weekend']
        ]
        X.append(features)
        y.append(row[target_col])
    return np.array(X), np.array(y)