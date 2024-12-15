import pandas as pd
from prophet import Prophet
import pickle

# load model
with open("bed_predictions_fake.pkl", "rb") as f:
    model = pickle.load(f)

# generates df with hours from 0 to 24
def create_hourly_dataframe():
    base_date = pd.Timestamp.now().normalize()  # Start from today's date, 00:00
    hours = [base_date + pd.to_timedelta(hour, unit='h') for hour in range(25)]  # From 0 to 24 hours
    return pd.DataFrame({"ds": hours})

future_df = create_hourly_dataframe()

forecast = model.predict(future_df)
forecast['yhat'] = forecast['yhat'].clip(lower=0, upper=1)
forecast['yhat_lower'] = forecast['yhat_lower'].clip(lower=0, upper=1)
forecast['yhat_upper'] = forecast['yhat_upper'].clip(lower=0, upper=1)

print(forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]])