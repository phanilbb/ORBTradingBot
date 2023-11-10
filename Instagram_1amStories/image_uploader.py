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


def get_all_albums():
    url = "https://api.imgur.com/3/account/phani1703/albums"
    headers = {
        'Authorization': 'Client-ID {}'.format(os.environ['imgur_client_id'])
    }

    r = requests.get(url, headers=headers)
    print("Album get response " + r.text)
    return r.json()


def get_album(topic):
    response = get_all_albums()
    default = None
    if 'success' in response and response['success'] and 'data' in response and response['data']:
        for each_album in response['data']:
            if each_album['title'].lower() == topic.lower():
                return each_album
            if each_album['title'].lower() == 'default':
                default = each_album

    return default


def get_album_data(album_id):
    url = "https://api.imgur.com/3/account/phani1703/album/{}".format(album_id)
    headers = {
        'Authorization': 'Client-ID {}'.format(os.environ['imgur_client_id'])
    }

    r = requests.get(url, headers=headers)
    print("Album ID get response " + r.text)
    return r.json()


def get_images_list(topic):
    album = get_album(topic)
    data = []
    if not album:
        return data

    response = get_album_data(album['id'])
    if 'success' in response and response['success'] and 'data' in response and response['data']:
        for each_image in response['data']['images']:
            data.append({
                'link': each_image['link'],
                'id': each_image['id']
            })

    return data
