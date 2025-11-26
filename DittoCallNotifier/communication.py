import requests
import datetime


class Communication:
    def __init__(self):
        self.bot_token = '5945431317:AAFzROpE5IpiuiJyJJyXdCp7prE5-EH7mOg'
        self.bot_chatId = '1170124746'
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    def is_session_id(self, text):
        if len(text) != 32:
            return False
        return text.isalnum() and text.islower()

    def send_telegram_msg(self, bot_message):
        send_text = f"{self.api_url}/sendMessage?chat_id={self.bot_chatId}&parse_mode=Markdown&text={bot_message}"
        response = requests.get(send_text)
        return response.json()

    def read_messages(self):
        url = f"{self.api_url}/getUpdates"
        resp = requests.get(url)
        return resp.json()

    def get_today_messages(self):
        """Return only today's messages."""
        updates = self.read_messages()
        today = datetime.date.today()

        today_messages = []

        for update in updates.get("result", []):
            msg = update.get("message") or update.get("edited_message")
            if not msg:
                continue

            ts = msg.get("date")
            msg_date = datetime.datetime.fromtimestamp(ts).date()

            if msg_date == today:
                today_messages.append(msg)

        return today_messages

    def get_today_session_id(self):
        """Return only today's messages."""
        updates = self.get_today_messages()

        for update in updates:

            text = update.get("text")
            if not text:
                continue

            if self.is_session_id(text):
                return text

        return None

    def delete_old_messages(self):
        updates = self.read_messages()
        today = datetime.date.today()

        last_id = None
        for update in updates.get("result", []):
            msg = update.get("message")
            if not msg:
                continue

            ts = msg.get("date")
            msg_date = datetime.datetime.fromtimestamp(ts).date()

            # Skip today's messages
            if msg_date == today:
                continue

            last_id = update['update_id'] + 1

        if last_id:
            requests.get(f"{self.api_url}/getUpdates?offset={last_id}")
