import functools
import json
import os.path as path
from config import baseDir


def subscribed_middleware(handler_function):
    @functools.wraps(handler_function)
    def middleware(update, context):
        with open(path.join(baseDir, 'subscribers.json')) as reader:
            subscribers = json.load(reader)

        chat_id = str(update.effective_chat.id)

        if chat_id not in subscribers:
            return context.bot.send_message(
                chat_id=update.effective_chat.id, text='You are not subscribed!')

        return handler_function(update, context)

    return middleware
