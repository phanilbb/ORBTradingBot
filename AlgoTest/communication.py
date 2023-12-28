import requests

BOT_TOKEN = '5945431317:AAFzROpE5IpiuiJyJJyXdCp7prE5-EH7mOg'
BOT_CHAT_ID = '1170124746'


def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + BOT_CHAT_ID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()
