# forecast.py
import numpy as np
import pandas as pd

def sliding_window_forecast(model, X_last, future_dates, X_mean, X_std, y_min, y_max, lag=5):
    """
    Predict N future steps using a sliding window approach.

    Parameters:
    - model: trained MLP model
    - X_last: last normalized input vector used for starting prediction
    - future_dates: list of future pd.Timestamp
    - X_mean/X_std: normalization vectors
    - y_min/y_max: for unnormalizing output
    - lag: number of lagged sales values used

    Returns:
    - list of forecasted actual sales values
    """
    y_preds = []
    current_input = X_last.tolist()

    for date in future_dates:
        y_next_norm = model.forward(current_input)
        y_preds.append(y_next_norm)

        # Slide the lag window
        new_lags = current_input[:lag][1:] + [y_next_norm]  # shift window forward

        # Extract date features
        dow = date.weekday()
        dom = date.day
        month = date.month
        is_weekend = 1 if dow >= 5 else 0

        # Cyclical encoding
        dow_sin = np.sin(2 * np.pi * dow / 7)
        dow_cos = np.cos(2 * np.pi * dow / 7)
        month_sin = np.sin(2 * np.pi * month / 12)
        month_cos = np.cos(2 * np.pi * month / 12)

        # Normalize date features using training mean/std (skip normalization for cyclical features)
        features = [
            dow_sin, dow_cos,
            (dom - X_mean[lag+2]) / X_std[lag+2],
            month_sin, month_cos,
            (is_weekend - X_mean[lag+5]) / X_std[lag+5]
        ]

        current_input = new_lags + features

    # Unnormalize predictions
    return [y * (y_max - y_min) + y_min for y in y_preds]
