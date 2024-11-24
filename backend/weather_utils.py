import requests

def get_weather_data(latitude=43.6158, longitude=13.5189):
    parameters = {
        'latitude': latitude,
        'longitude': longitude,
        'hourly': 'temperature_2m,precipitation_probability,cloudcover',
        'start': 'auto',
        'end': 'next1hours',
        'timezone': 'auto'
    }

    api_url = 'https://api.open-meteo.com/v1/forecast'

    response = requests.get(api_url, params=parameters)

    if response.status_code == 200:
        data = response.json()
        hourly_data = data.get('hourly', {})

        time = hourly_data.get('time', [])[0]
        temperature = hourly_data.get('temperature_2m', [])[0]
        precipitation_probability = hourly_data.get('precipitation_probability', [])[0]
        cloud_cover = hourly_data.get('cloudcover', [])[0]

        if precipitation_probability > 50:
            weather_condition = "Rainy"
        elif cloud_cover < 30:
            weather_condition = "Sunny"
        elif cloud_cover >= 30 and cloud_cover <= 70:
            weather_condition = "Partly Cloudy"
        else:
            weather_condition = "Cloudy"

        return weather_condition
    else:
        print(f"Failed to retrieve data, status code: {response.status_code}")
        return None
