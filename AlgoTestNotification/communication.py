import requests


class Communication:
    bot_token = None
    bot_chatId = None

    def __init__(self):
        self.bot_token = '7000080684:AAEE4Rrx_RkfCsB8sLXCyXWyxet2PQBLHKo'
        self.bot_chatId = '-4594468620'

    def send_telegram_msg(self, bot_message):
        send_text = 'https://api.telegram.org/bot' + self.bot_token + '/sendMessage?chat_id=' + self.bot_chatId + '&parse_mode=Markdown&text=' + bot_message
        response = requests.get(send_text)
        return response.json()

    def send_telegram_photo(self, photo_url, caption=None):
        send_text = f'https://api.telegram.org/bot{self.bot_token}/sendPhoto'
        payload = {
            'chat_id': self.bot_chatId,
            'photo': photo_url
        }
        if caption:
            payload['caption'] = caption

        response = requests.post(send_text, data=payload)
        return response.json()
