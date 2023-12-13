import json
import os
import time
import reels
import requests

import caption_generator
import communication
import content_generator
import image_editor
import s3
from helpers import constants


def upload(s3_image_path, caption):
    try:
        ig_user_id = os.environ['ig_user_id']
        access_token = os.environ['ig_access_token']
        post_url = 'https://graph.facebook.com/v18.0/{}/media'.format(ig_user_id)

        payload = {
            'image_url': s3.get_public_url(s3_image_path),
            'caption': caption,
            'access_token': access_token,
            'location_id': constants.INDIA_LOCATION_ID
        }

        r = requests.post(post_url, data=payload)
        results = json.loads(r.text)
        print("Media response : " + json.dumps(r.json()))
        if 'id' in results:
            creation_id = results['id']
            second_url = 'https://graph.facebook.com/v18.0/{}/media_publish'.format(ig_user_id)
            second_payload = {
                'creation_id': creation_id,
                'access_token': access_token
            }
            r = requests.post(second_url, data=second_payload)
            print(r.text)
            print("Image published to instagram")
        else:
            print("image posting not possible")
    except Exception as e:
        print(e)
        communication.telegram_bot_sendtext("Image failed to post to instagram : " + str(e))


def new_post():
    content = content_generator.get_text_from_sheet(constants.CONTENT_SHEET)
    caption = caption_generator.generate_caption(content)
    content['Title'] = None  # for normal post, title is not required.
    image_path = image_editor.make_image(content)
    key = s3.upload_file(image_path, '/tmp', '{}.jpg'.format(str(round(time.time() * 1000))))
    print("Public url for key {} is {}".format(key, s3.get_public_url(key)))
    if os.environ.get("env", "aws") != "local":
        upload(key, caption)
        os.remove(image_path)
        s3.delete_file(key)
        content_generator.backup_and_delete(constants.CONTENT_SHEET, constants.CONTENT_UPLOADED_SHEET, content['row'])
