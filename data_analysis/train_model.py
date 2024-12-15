'''
Train model on real data from the alarm.
'''
import pandas as pd
from prophet import Prophet
import pickle

def train_save_model(data, model_path="bed_predictions.pkl"):
    # train
    model = Prophet(changepoint_prior_scale=0.01, daily_seasonality=True, weekly_seasonality=False, yearly_seasonality=False)
    model.add_seasonality(name='daily', period=24, fourier_order=10, prior_scale=5)
    model.fit(data)

    # save
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {model_path}.")

if __name__ == "__main__":
    data = pd.read_csv("train_data.csv")
    data['ds'] = pd.to_datetime(data['ds'])
    data['ds'] = data['ds'].dt.tz_localize(None)

    model_path = "bed_predictions.pkl"
    train_save_model(data, model_path)
