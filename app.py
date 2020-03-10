from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
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


def location(update, context):
    with open(path.join(baseDir, 'subscribers.json')) as reader:
        subscribers = json.load(reader)

    longitude = update.message.location.longitude
    latitude = update.message.location.latitude
    subscribers[update.effective_chat.id] = {
        'longitude': longitude, 'latitude': latitude}

    with open(path.join(baseDir, 'subscribers.json'), 'w') as writer:
        json.dump(subscribers, writer)

    context.bot.send_message(
        chat_id=update.effective_chat.id, text='Subscribed successfully!')



# Creating the Handlers
start_handler = CommandHandler('start', start)
subscribe_handler = CommandHandler('subscribe', subscribe)
location_handler = MessageHandler(Filters.location, location)

# Adding the handlers to the dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(subscribe_handler)
dispatcher.add_handler(location_handler)

updater.start_polling()
updater.idle()
