import json
import requests
import os.path as path
from config import baseDir, API_KEY
from datetime import date, timedelta


def create_weather_endpoint(lat, lon, count):
    return "https://api.openweathermap.org/data/2.5/forecast?lat={0}&lon={1}&cnt={2}&APPID={3}&units=metric".format(lat, lon, count, API_KEY)


def call_weather_endpoint(chat_id, count):
    with open(path.join(baseDir, 'subscribers.json')) as reader:
        subscribers = json.load(reader)
        current_user = subscribers[chat_id]

    lat = current_user['latitude']
    lon = current_user['longitude']
    endpoint = create_weather_endpoint(lat, lon, count)
    response = requests.get(endpoint)

    return create_weather_response(response.json()['list'], count)


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
    humidity = response[3]['main']['humidity']
    wind = response[3]['wind']['speed']

    alert = {'main_description':main_description, 'sub_description':sub_description, 'temp':temp,
            'humidity':humidity, 'wind':wind}

    alerts[str(chat_id)] = alert

    with open(path.join(baseDir, 'alerts.json'), 'w') as writer:
        json.dump(alerts, writer)


def create_weather_response(response, count):
    today = date.today()
    text = ''
    i = 0
    days_iterator = 1

    while i < len(response):
        next_day = today + timedelta(days=days_iterator)
        formatted_next_day = next_day.strftime('%B %d, %Y')
        weather = response[i]['weather'][0]
        main = response[i]['main']
        wind = response[i]['wind']

        text = text + "{0}\n{1} - {2}\ntemperature - {3}\u2103\nhumidity - {4}%\nwind - {5}km/h\n\n".format(str(formatted_next_day), weather['main'].lower(), weather['description'],
            main['temp'], main['humidity'], wind['speed'])

        i += 8
        days_iterator += 1

    return text


def create_alert_text(alert):
    today = date.today()
    return "Good morning, here is the weather forecast for today, {0}\n\n{1} - {2}\ntemperature - {3}\u2103\nhumidity - {4}%\nwind - {5}km/h\n\n".format(today.strftime('%B %d, %Y'), alert['main_description'], alert['sub_description'],
        alert['temp'], alert['humidity'], alert['wind'] )

