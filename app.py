from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from geopy.geocoders import Nominatim
import os.path as path
import logging
import json


# Enable logging of errors
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

baseDir = path.abspath(path.dirname('__file__'))

# initializing relevant variables
updater = Updater(
    token='1087869624:AAGXcFIAHqVtrN2NNBtRTXwrjDAaDZjfMyo', use_context=True)
dispatcher = updater.dispatcher
job = updater.job_queue


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



# Creating the Handlers
start_handler = CommandHandler('start', start)
subscribe_handler = CommandHandler('subscribe', subscribe)
unsubscribe_handler = CommandHandler('unsubscribe', unsubscribe)
view_location_handler = CommandHandler('location', view_location)
set_location_handler = MessageHandler(Filters.location, set_location)
changelocation_handler = CommandHandler('changelocation', change_location)

# Adding the handlers to the dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(subscribe_handler)
dispatcher.add_handler(unsubscribe_handler)
dispatcher.add_handler(view_location_handler)
dispatcher.add_handler(set_location_handler)
dispatcher.add_handler(changelocation_handler)

updater.start_polling()
updater.idle()
