import numpy as np
from atrax import Atrax as tx

def create_lagged_dataset(ds, date_col='sale_date', target_col='sales', lag=5):
    """Create a lagged dataset for time series forecasting.
    
    Parameters:
        ds (pd.DataFrame): DataFrame containing the time series data.
        date_col (str): The name of the date column in the DataFrame.
        target_col (str): The name of the target column to forecast.
        lag (int): The number of lagged observations to include.
        
    Returns:
        X (tx.Series): Array of lagged features.
        y (tx.Series): Array of target values."""
    X, y = [], []
    try:
        ds[date_col] = tx.to_datetime(ds[date_col])
        ds = ds.sort(date_col)

        ds['day_of_week'] = ds[date_col].dt.weekday
        ds['is_weekend'] = ds['day_of_week'].isin([5, 6])
        ds['day_of_month'] = ds[date_col].dt.day
        ds['month'] = ds[date_col].dt.month    


        for i in range(lag, ds.shape()[0]):
            lagged_values = [d.strftime('%m/%d/%Y') for d in ds[date_col].values[i - lag:i]]
            row = ds.loc[i]
            features = lagged_values + [
                row['day_of_week'].values[0],
                row['day_of_month'].values[0],
                row['month'].values[0],
                row['is_weekend'].values[0]
            ]
            X.append(features)
            y.append(row[target_col])
        return tx.Series(X), tx.Series(y)
    except Exception as e:
        raise ValueError(f"Error processing dataset: {e}")
