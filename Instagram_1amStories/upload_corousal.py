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
import copy


def upload_get_container_id(s3_image_paths, caption):
    child_container_ids = []
    try:
        ig_user_id = os.environ['ig_user_id']
        access_token = os.environ['ig_access_token']
        post_url = 'https://graph.facebook.com/v18.0/{}/media'.format(ig_user_id)

        for s3_image_path in s3_image_paths:
            payload = {
                'is_carousel_item': True,
                'image_url': s3.get_public_url(s3_image_path),
                'caption': caption,
                'access_token': access_token,
                'location_id': constants.INDIA_LOCATION_ID
            }
            r = requests.post(post_url, data=payload)
            results = json.loads(r.text)
            print("Media response : " + json.dumps(r.json()))
            if 'id' in results:
                child_container_ids.append(results['id'])
        return child_container_ids

    except Exception as e:
        print(e)
        communication.telegram_bot_sendtext("Carousel failed to post to instagram : " + str(e))
    return child_container_ids


def upload(s3_image_paths, caption):
    child_ids = upload_get_container_id(s3_image_paths, caption)
    try:
        ig_user_id = os.environ['ig_user_id']
        access_token = os.environ['ig_access_token']
        post_url = 'https://graph.facebook.com/v18.0/{}/media'.format(ig_user_id)

        print("Publishing child IDs : " + str(child_ids))
        payload = {
            'media_type': 'CAROUSEL',
            'children': child_ids,
            'access_token': access_token,
            'caption': caption,
            'location_id': constants.INDIA_LOCATION_ID
        }

        r = requests.post(post_url, json=payload)
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
            print("Carousel published to instagram")
        else:
            print("Carousel posting not possible")
    except Exception as e:
        print(e)
        communication.telegram_bot_sendtext("Carousel failed to post to instagram : " + str(e))


def new_carousel():
    content = content_generator.get_text_from_sheet(constants.CONTENT_SHEET)
    caption = caption_generator.generate_caption(content)
    image = image_editor.get_images(content['Category'])
    image_paths = [get_title_image(content, copy.deepcopy(image)), get_content_image(content, copy.deepcopy(image))]

    keys = []
    for image_path in image_paths:
        key = s3.upload_file(image_path, '/tmp', '{}.jpg'.format(str(len(keys) + 1)))
        keys.append(key)

    if os.environ.get("env", "aws") != "local":
        upload(keys, caption)
        [os.remove(image_path) for image_path in image_paths]
        [s3.delete_file(key) for key in keys]
        content_generator.backup_and_delete(constants.CONTENT_SHEET, constants.CONTENT_UPLOADED_SHEET, content['row'])


def get_title_image(content, image):
    data = copy.deepcopy(content)
    data['Content'] = None
    return image_editor.image_editor(image, "{}.jpg".format(str(round(time.time() * 1000))), data,
                                     logo_text=constants.LOGO_TEXT_COROUSAL)


def get_content_image(content, image):
    data = copy.deepcopy(content)
    data['Title'] = None
    return image_editor.image_editor(image, "{}.jpg".format(str(round(time.time() * 1000))), data,
                                     logo_text=constants.LOGO_TEXT)
