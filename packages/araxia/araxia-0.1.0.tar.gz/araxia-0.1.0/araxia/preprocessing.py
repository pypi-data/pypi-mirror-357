import numpy as np

def create_dataset_with_date_features(sales, dates, lag=3):
    X, y = [], []
    for i in range(lag, len(sales)):
        lags = sales[i-lag:i]
        date = dates[i]
        dow = date.weekday()
        dom = date.day
        month = date.month
        is_weekend = 1 if dow >= 5 else 0

        features = lags + [dow, dom, month, is_weekend]
        X.append(features)
        y.append(sales[i])
    return np.array(X), np.array(y)

def create_dataset_with_onehot_dow(sales, dates, lag=3):
    X, y = [], []
    for i in range(lag, len(sales)):
        lags = sales[i - lag:i]
        date = dates[i]
        dow = date.weekday()
        onehot_dow = [1 if j == dow else 0 for j in range(7)]
        dom = date.day
        month = date.month
        is_weekend = 1 if dow >= 5 else 0
        features = lags + onehot_dow + [dom, month, is_weekend]
        X.append(features)
        y.append(sales[i])
    return np.array(X), np.array(y)


# Recreate the lagged dataset with cyclical features instead of raw weekday/month
def create_dataset_with_cyclic_features(df, lag=5):
    X, y = [], []
    for i in range(lag, len(df)):
        lagged_sales = df["sales"].values[i - lag:i].tolist()
        row = df.iloc[i]
        features = lagged_sales + [
            row["dow_sin"], row["dow_cos"],
            row["day_of_month"],
            row["month_sin"], row["month_cos"],
            row["is_weekend"]
        ]
        X.append(features)
        y.append(row["sales"])
    return np.array(X), np.array(y)

def create_lagged_dataset(ds, lag=5):
    X, y = [], []
    for i in range(lag, len(ds)):
        lagged_sales = ds['sales'].values[i - lag:i].tolist()
        row = ds.iloc[i]
        features = lagged_sales + [
            row['day_of_week'],
            row['day_of_month'],
            row['month'],
            row['is_weekend']
        ]
        X.append(features)
        y.append(row['sales'])
    return np.array(X), np.array(y)