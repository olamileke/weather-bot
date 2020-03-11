from telegram import KeyboardButton, ReplyKeyboardMarkup, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from geopy.geocoders import Nominatim
from datetime import time
from config import baseDir, BOT_TOKEN
from endpoints import call_weather_endpoint, call_alert_endpoint, create_alert_text
import logging
import os.path as path
import json


# Enable logging of errors
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


# initializing relevant variables
updater = Updater(
    token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher
job = updater.job_queue
acceptable_forecasts = ['1', '2', '3', '4', '5']


# Handler Functions
def start(update, context):
    with open(path.join(baseDir, 'start_message.txt')) as reader:
        text = reader.read()

    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def subscribe(update, context):
    with open(path.join(baseDir, 'subscribers.json')) as reader:
        subscribers = json.load(reader)

    if str(update.effective_chat.id) not in subscribers:
        location_keyboard = KeyboardButton(
            text='Share Location', request_location=True)
        custom_keyboard = [[location_keyboard]]
        reply_markup = ReplyKeyboardMarkup(
            custom_keyboard, resize_keyboard=True)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Would you mind sharing your location with me?', reply_markup=reply_markup)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text='You are already subscribed!')


def unsubscribe(update, context):
    chat_id = str(update.effective_chat.id)

    with open(path.join(baseDir, 'subscribers.json')) as reader:
        subscribers = json.load(reader)

    del(subscribers[chat_id])

    with open(path.join(baseDir, 'subscribers.json'), 'w') as writer:
        json.dump(subscribers, writer)

    context.bot.send_message(
        chat_id=chat_id, text='Unsubscribed successfully!')


def set_location(update, context):
    with open(path.join(baseDir, 'subscribers.json')) as reader:
        subscribers = json.load(reader)

    with open(path.join(baseDir, 'subscribed.txt')) as reader:
        text = reader.read()

    chat_id = str(update.effective_chat.id)
    longitude = update.message.location.longitude
    latitude = update.message.location.latitude

    if chat_id in subscribers:
        text = 'Location updated successfully!'
        subscribers[chat_id]['latitude'] = latitude
        subscribers[chat_id]['longitude'] = longitude
    else:
        subscribers[chat_id] = {
            'latitude': latitude, 'longitude': longitude}

    with open(path.join(baseDir, 'subscribers.json'), 'w') as writer:
        json.dump(subscribers, writer)

    context.bot.send_message(
        chat_id=chat_id, text=text)


def view_location(update, context):
    with open(path.join(baseDir, 'subscribers.json')) as reader:
        subscribers = json.load(reader)

    current_user = subscribers[str(update.effective_chat.id)]

    geolocator = Nominatim(user_agent='theweatheralert_bot')
    location = geolocator.reverse("{0}, {1}".format(
        current_user['latitude'], current_user['longitude']))

    context.bot.send_message(
        chat_id=update.effective_chat.id, text=location.address)


def change_location(update, context):
    location_keyboard = KeyboardButton(
        text='Share Location', request_location=True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='share your new location with me', reply_markup=reply_markup)


def forecast(update, context):
    chat_id = str(update.effective_chat.id)

    if len(context.args) != 1:
        context.bot.send_message(
            chat_id=chat_id, text='Please input a number from 1-5 after the command')
        return

    if context.args[0] not in acceptable_forecasts:
        context.bot.send_message(
            chat_id=chat_id, text='Please input a number from 1-5 after the command')
        return

    context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    text = call_weather_endpoint(chat_id, int(context.args[0]) * 8)

    context.bot.send_message(chat_id=chat_id, text=text)


# Job Functions
def fetch_alerts(context):
    with open(path.join(baseDir, 'subscribers.json')) as reader:
        subscribers = json.load(reader)

    for chat_id, coordinates in subscribers.items():
        call_alert_endpoint(chat_id, coordinates, 8)


def send_alerts(context):
    with open(path.join(baseDir, 'alerts.json')) as reader:
        alerts = json.load(reader)

    for chat_id, alert in alerts.items():
        context.bot.send_message(chat_id=chat_id, text=create_alert_text(alert))


job.run_daily(fetch_alerts, time=time(hour=22, minute=27, second=50))
job.run_daily(send_alerts, time=time(hour=23, minute=19, second=50))


# Creating the Handlers
start_handler = CommandHandler('start', start)
subscribe_handler = CommandHandler('subscribe', subscribe)
unsubscribe_handler = CommandHandler('unsubscribe', unsubscribe)
view_location_handler = CommandHandler('location', view_location)
set_location_handler = MessageHandler(Filters.location, set_location)
changelocation_handler = CommandHandler('changelocation', change_location)
forecast_handler = CommandHandler('forecast', forecast)

# Adding the handlers to the dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(subscribe_handler)
dispatcher.add_handler(unsubscribe_handler)
dispatcher.add_handler(view_location_handler)
dispatcher.add_handler(set_location_handler)
dispatcher.add_handler(changelocation_handler)
dispatcher.add_handler(forecast_handler)

updater.start_polling()
updater.idle()
