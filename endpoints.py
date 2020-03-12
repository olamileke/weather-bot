import json
import requests
import os.path as path
from config import baseDir, API_KEY
from datetime import date, timedelta


def create_weather_endpoint(lat, lon, count):
    return "https://api.openweathermap.org/data/2.5/forecast?lat={0}&lon={1}&cnt={2}&APPID={3}&units=metric".format(lat, lon, count, API_KEY)


def call_forecast_endpoint(chat_id, count):
    with open(path.join(baseDir, 'subscribers.json')) as reader:
        subscribers = json.load(reader)
        current_user = subscribers[chat_id]

    lat = current_user['latitude']
    lon = current_user['longitude']
    endpoint = create_weather_endpoint(lat, lon, count)
    response = requests.get(endpoint)

    return create_forecast_response(response.json()['list'], count)


def call_alert_endpoint(chat_id, coordinates, count):
    lat = coordinates['latitude']
    lon = coordinates['longitude']
    endpoint = create_weather_endpoint(lat, lon, count)
    response = requests.get(endpoint)

    create_alerts(chat_id, response.json()['list'])


def create_alerts(chat_id, response):
    with open(path.join(baseDir, 'alerts.json')) as reader:
        alerts = json.load(reader)

    main_description = response[3]['weather'][0]['main'].lower()
    sub_description = response[3]['weather'][0]['description']
    temp = response[3]['main']['temp']
    max_temp = response[3]['main']['temp_max']
    min_temp = response[3]['main']['temp_min']
    humidity = response[3]['main']['humidity']
    wind_speed = response[3]['wind']['speed']
    wind_degree = response[3]['wind']['deg']

    alert = {'main_description': main_description, 'sub_description': sub_description, 'temp': temp,
             'max_temp': max_temp, 'min_temp': min_temp, 'humidity': humidity, 'wind_speed': wind_speed, 'wind_degree': wind_degree}

    alerts[str(chat_id)] = alert

    with open(path.join(baseDir, 'alerts.json'), 'w') as writer:
        json.dump(alerts, writer)


def create_forecast_response(response, count):
    today = date.today()
    text = ''
    i = 0
    days_iterator = 1

    while i < len(response):
        next_day = today + timedelta(days=days_iterator)
        formatted_next_day = next_day.strftime('%B %d, %Y')
        main_description = response[i]['weather'][0]['main'].lower()
        sub_description = response[i]['weather'][0]['description']
        max_temp = response[i]['main']['temp_max']
        min_temp = response[i]['main']['temp_min']
        temp = response[i]['main']['temp']
        humidity = response[i]['main']['humidity']
        speed = response[i]['wind']['speed']
        deg = response[i]['wind']['deg']

        text = text + "{0}\n{1} - {2}\nhighest temperature - {3}\u2103\ntemperature - {4}\u2103\nlowest temperature - {5}\u2103\nhumidity - {6}%\nwind speed - {7}km/h\nwind degree - {8}\u00B0\n\n".format(
            str(formatted_next_day), main_description, sub_description, max_temp, temp, min_temp, humidity, speed, deg)

        i += 8
        days_iterator += 1

    return text


def create_alert_text(alert):
    today = date.today()
    return '''Good morning. Here is the weather forecast for today - {0}\n{1} - {2}\nhighest temperature - {3}\u2103\ntemperature - {4}\u2103\nlowest temperature - {5}\u2103\nhumidity - {6}%\nwind speed - {7}km/h\nwind degree - {8}\u00B0\n\n'''.format(today.strftime('%B %d, %Y'), alert['main_description'],
                                                                                                                                                                                                                                                            alert['sub_description'], alert['max_temp'], alert['temp'], alert['min_temp'], alert['humidity'], alert['wind_speed'], alert['wind_degree'])
