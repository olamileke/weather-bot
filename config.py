import os.path as path

def create_formatted_endpoint(lat, lon, count):
    return "https://api.openweathermap.org/data/2.5/forecast?lat={0}&lon={1}&cnt={2}&APPID={3}".format(lat, lon, count, API_KEY)


BOT_TOKEN = "1087869624:AAGXcFIAHqVtrN2NNBtRTXwrjDAaDZjfMyo"
API_KEY = "04805aacf38a86e7644bc839b288ab00"
baseDir = path.abspath(path.dirname('__file__'))
