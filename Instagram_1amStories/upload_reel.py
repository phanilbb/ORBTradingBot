import json
import os
import time
import reels
import requests

import caption_generator
import communication
import content_generator
import s3
from helpers import constants


def new_reel():
    content = content_generator.get_text_from_sheet(constants.CONTENT_SHEET)
    audio_path = reels.get_audio_file(content['Category'])
    video_path = reels.get_video()
    caption = caption_generator.generate_caption(content)
    video_path = reels.create_video(content, "image", video_path, audio_path, "video")
    key = s3.upload_file(video_path, '/tmp', '{}.mp4'.format(str(round(time.time() * 1000))))
    print("Public url for key {} is {}".format(key, s3.get_public_url(key)))
    if os.environ.get("env", "aws") != "local":
        upload(key, caption)
        os.remove(video_path)
        s3.delete_file(key)
        content_generator.backup_and_delete(constants.CONTENT_SHEET, constants.CONTENT_UPLOADED_SHEET, content['row'])


def upload(video_path, caption):
    try:
        ig_user_id = os.environ['ig_user_id']
        access_token = os.environ['ig_access_token']
        post_url = 'https://graph.facebook.com/v18.0/{}/media'.format(ig_user_id)
        payload = {
            'video_url': s3.get_public_url(video_path),
            'caption': caption,
            'access_token': access_token,
            'media_type': 'REELS',
            'share_to_feed': True
        }

        r = requests.post(post_url, data=payload)
        results = json.loads(r.text)
        print("Media response : " + json.dumps(r.json()))
        if 'id' in results:
            creation_id = results['id']
            wait_till_finished(creation_id)
            second_url = 'https://graph.facebook.com/v18.0/{}/media_publish'.format(ig_user_id)
            second_payload = {
                'creation_id': creation_id,
                'access_token': access_token
            }
            r = requests.post(second_url, data=second_payload)
            print(r.text)
            print("Reel published to instagram")
        else:
            print("Reel posting not possible")
    except Exception as e:
        print(e)
        communication.telegram_bot_sendtext("Reel failed to post to instagram : " + str(e))


def wait_till_finished(id):
    get_url = 'https://graph.facebook.com/v18.0/{}'.format(id)
    access_token = os.environ['ig_access_token']
    params = {
        'fields': 'status_code',
        'access_token': access_token
    }
    for i in range(0, 10):
        response = requests.get(get_url, params=params)
        response = response.json()
        if response['status_code'] == 'FINISHED':
            print("Reel upload finished")
            return True
        time.sleep(10)

    print("Reel upload failed")
    return False
