import json
import shutil
import os
import image_editor
import requests
import content_generator
import caption_generator
import imgur
import communication
import reels_maker


def get_images(start_directory):
    os.chdir('tmp')
    directory = os.listdir(os.curdir)
    if not directory:
        return None
    image = directory[0]
    shutil.move(image, start_directory)
    os.chdir(start_directory)
    return image


def upload(image, caption):
    image_upload_data = {}
    try:
        ig_user_id = os.environ['ig_user_id']
        access_token = os.environ['ig_access_token']
        post_url = 'https://graph.facebook.com/v18.0/{}/media'.format(ig_user_id)
        image_upload_data = imgur.upload_image(image)
        if not image_upload_data:
            print("image hosting failed")
            return

        payload = {
            'image_url': image_upload_data['link'],
            'caption': caption,
            'access_token': access_token,
            'location_id': 109524955741121
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
            content_generator.delete_row()
        else:
            print("image posting not possible")
    except Exception as e:
        print(e)
        communication.telegram_bot_sendtext("Image failed to post to instagram : " + str(e))
    finally:
        os.remove(image)
        if 'deletehash' in image_upload_data:
            imgur.delete(image_upload_data['deletehash'])


def new_post():
    text, topic, author = content_generator.get_text_from_sheet()
    caption = caption_generator.generate_caption(text, topic, author)
    image_paths = image_editor.make_image(text, topic)
    if os.environ.get("env", "aws") != "local":
        for image_path in image_paths:
            upload(image_path, caption)


def new_reel():
    audio_path = reels_maker.get_audio_file()
    video_path = reels_maker.get_video()
    text, topic, author = content_generator.get_text_from_sheet()
    caption = caption_generator.generate_caption(text, topic, author)
    video_path = reels_maker.create_video(text, "image", video_path, audio_path, "video")
    if os.environ.get("env", "aws") != "local":
        reels_maker.upload(video_path, caption)
