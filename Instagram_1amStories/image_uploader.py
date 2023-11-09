import base64
import os
import requests
import communication


def upload(image):
    with open(image, "rb") as file:
        url = "https://api.imgur.com/3/image"
        headers = {
            'Authorization': 'Client-ID {}'.format(os.environ['imgur_client_id'])
        }
        payload = {
            "image": base64.b64encode(file.read()),
        }
        try:
            r = requests.post(url, data=payload, headers=headers)
            print("Image upload response " + r.text)
            response = r.json()
            if 'success' in response and response['success']:
                return response['data']
            else:
                communication.telegram_bot_sendtext("Image failed to upload to imgur with success false")
            return {}
        except Exception as e:
            communication.telegram_bot_sendtext("Image failed to upload to imgur : " + str(e))


def delete(delete_hash):
    url = "https://api.imgur.com/3/image/{}".format(delete_hash)

    headers = {
        'Authorization': 'Client-ID {}'.format(os.environ['imgur_client_id'])
    }

    r = requests.delete(url, headers=headers)
    print("Image delete response " + r.text)
    return True
