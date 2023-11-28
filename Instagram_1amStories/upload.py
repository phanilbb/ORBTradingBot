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
import s3


def get_images(start_directory):
    os.chdir('tmp')
    directory = os.listdir(os.curdir)
    if not directory:
        return None
    image = directory[0]
    shutil.move(image, start_directory)
    os.chdir(start_directory)
    return image


def upload(s3_image_path, caption):
    try:
        ig_user_id = os.environ['ig_user_id']
        access_token = os.environ['ig_access_token']
        post_url = 'https://graph.facebook.com/v18.0/{}/media'.format(ig_user_id)

        payload = {
            'image_url': s3.get_public_url(s3_image_path),
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


def upload_to_s3(local_file_path, folder, file_name):
    folder = folder.split('/')[1]
    s3.upload_file(local_file_path, folder, file_name)
    response = s3.get_folder_objects(folder)
    return s3.fetch_keys(response, '.{}'.format(file_name.split('.')[1]))


def new_post():
    text, topic, author = content_generator.get_text_from_sheet()
    caption = caption_generator.generate_caption(text, topic, author)
    image_paths = image_editor.make_image(text, topic)
    keys = upload_to_s3(image_paths[0], '/tmp', 'post.jpg')
    print("Public url for key {} is {}".format(keys[0], s3.get_public_url(keys[0])))
    if os.environ.get("env", "aws") != "local":
        upload(keys[0], caption)
        os.remove(image_paths[0])
        for key in keys:
            s3.delete_file(key)


def new_reel():
    text, topic, author = content_generator.get_text_from_sheet()
    audio_path = reels_maker.get_audio_file(topic)
    video_path = reels_maker.get_video()
    caption = caption_generator.generate_caption(text, topic, author)
    video_path = reels_maker.create_video(text, "image", video_path, audio_path, "video")
    keys = upload_to_s3(video_path, '/tmp', 'reel.mp4')
    print("Public url for key {} is {}".format(keys[0], s3.get_public_url(keys[0])))
    if os.environ.get("env", "aws") != "local":
        reels_maker.upload(keys[0], caption)
        os.remove(video_path)
        for key in keys:
            s3.delete_file(key)
