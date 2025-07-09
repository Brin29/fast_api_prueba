import numpy as np
import pandas as pd
from .loader import model, scaler
from .preprocessing import scale_dataframe

WINDOW_SIZE = 2
PREDICT_YEARS = 11

def predict_future(df: pd.DataFrame):
    scaled_df = scale_dataframe(df, scaler)
    last_sequence = scaled_df.iloc[-WINDOW_SIZE:].values
    last_sequence = np.expand_dims(last_sequence, axis=0)

    predicted_scaled = model.predict(last_sequence)
    predicted_scaled = predicted_scaled.reshape(PREDICT_YEARS, scaled_df.shape[1])
    predicted = scaler.inverse_transform(predicted_scaled)

    last_year = int(df.index[-1])
    future_years = [last_year + i for i in range(1, PREDICT_YEARS + 1)]

    result = []
    for i, year in enumerate(future_years):
        result.append({
            "year": year,
            "values": {
                col: float(predicted[i][j]) for j, col in enumerate(df.columns)
            }
        })

    return result