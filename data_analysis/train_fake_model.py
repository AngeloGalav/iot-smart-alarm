'''
Trains a model on fake data.
'''
from prophet import Prophet
import pandas as pd
import pickle

# data
data = {
    'ds': pd.date_range(start='2024-10-10', periods=1000, freq='H'),
    'y': [1 if (0 <= hour % 24 <= 5) or (21 <= hour % 24 <= 23) else 0 for hour in range(1000)]
}
df = pd.DataFrame(data)

model = Prophet(changepoint_prior_scale=0.01, daily_seasonality=True, weekly_seasonality=False, yearly_seasonality=False)
model.add_seasonality(name='daily', period=24, fourier_order=10, prior_scale=5)
model.fit(df)

with open('bed_predictions_fake.pkl', 'wb') as f:
    pickle.dump(model, f)

future = model.make_future_dataframe(periods=48, freq='H')
forecast = model.predict(future)

# clip limits
forecast['yhat'] = forecast['yhat'].clip(lower=0, upper=1)
forecast['yhat_lower'] = forecast['yhat_lower'].clip(lower=0, upper=1)
forecast['yhat_upper'] = forecast['yhat_upper'].clip(lower=0, upper=1)

fig = model.plot(forecast)
fig.savefig('adjusted_forecast_plot.png')
