import json
import requests
import os.path as path
from config import baseDir, API_KEY
from datetime import date, timedelta


def create_formatted_endpoint(lat, lon, count):
    return "https://api.openweathermap.org/data/2.5/forecast?lat={0}&lon={1}&cnt={2}&APPID={3}".format(lat, lon, count, API_KEY)


def call_forecast_endpoint(chat_id, count):
    with open(path.join(baseDir, 'subscribers.json')) as reader:
        subscribers = json.load(reader)
        current_user = subscribers[chat_id]

    lat = current_user['latitude']
    lon = current_user['longitude']

    endpoint = create_formatted_endpoint(lat, lon, count)

    response = requests.get(endpoint)

    return create_forecast_response(response.json()['list'], count)


def create_forecast_response(response, count):
    today = date.today()
    text = ''
    i = 0
    days_iterator = 1

    while i < len(response):
        next_day = today + timedelta(days=days_iterator)
        formatted_next_day = next_day.strftime('%d/%m/%Y')
        text = text + '''{0}\n{1} - {2}\nTemperature - {3}\nHumidity - {4}\n\n'''.format(str(formatted_next_day),
        	response[i]['weather'][0]['main'], response[i]['weather'][0]['description'], 
        	response[i]['main']['temp'], response[i]['main']['humidity'])
        i += 8
        days_iterator += 1

    return text
