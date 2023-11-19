import os
import random
import time

import background_selector
import requests
import subprocess
import re
from PIL import Image, ImageDraw, ImageFont
from string import ascii_letters
import textwrap
import sys
import imgur
import content_generator
import json
import communication
import caption_generator


def get_audio_file():
    audio_files = [f"audio/{file}" for file in os.listdir("audio") if file.endswith(".mp3")]
    random.shuffle(audio_files)
    return audio_files[0]


def get_video():
    image_data = imgur.get_images_list("reels")
    index = background_selector.get_background_index("reels", len(image_data) - 1)
    file = image_data[index]
    tmp_dir = '/tmp'
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    file_path = tmp_dir + "/downloaded_file.mp4"
    if download_mp4(file['link'], file_path):
        return file_path
    return None


def download_mp4(url, save_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Download completed. File saved at: {save_path}")
        return True
    else:
        print(f"Failed to download. Status code: {response.status_code}")

    return False


def create_video(text, text_name, video_file, audio_file, file_name):
    image_text_source_y = 700
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height', '-of', 'csv=p=0:s=x', video_file],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    video_size = re.findall('\d+', result.stdout.decode())[0:2]
    video_width, video_height = map(int, video_size)

    # Get video duration
    ffprobe_command = f'ffprobe -i "{video_file}" -show_entries format=duration -v quiet -of csv="p=0"'
    video_duration = subprocess.check_output(ffprobe_command, shell=True)
    video_duration = float(video_duration.decode('utf-8').strip())

    # Set the start time of text
    text_start_time = 0
    # Create image of verse
    created_verse_image_data = create_image(text, (int(video_width), int(video_height / 2)), text_name)
    created_verse_image = created_verse_image_data[0]

    text2_y: int = image_text_source_y

    output_path = '/tmp'
    if output_path and not os.path.exists(output_path):
        os.makedirs(output_path)
        output_path = output_path + "/{}.mp4".format(file_name)
    else:
        output_path = "{}.mp4".format(file_name)

    ffmpeg_command = (
        'ffmpeg -loglevel error -stats -y -i "{}" '
        '-i "{}" -i "{}" -r 24 -filter_complex '
        '"[1:v]eq=brightness=-0.1[v1]; '
        '[v1][2:v]overlay=(W-w)/2:{}:enable=\'between(t,{},{})\'[v2]" '
        '-t {} -map "[v2]" -map 0 -c:v libx264 -preset veryfast -crf 18 "{}"'
    ).format(
        audio_file, video_file, created_verse_image,
        text2_y, text_start_time, video_duration,
        video_duration, output_path
    )

    try:
        subprocess.call(ffmpeg_command, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        sys.exit()
    except FileNotFoundError as e:
        print(f"An error occurred: {e}")
        sys.exit()

    return output_path


def create_image(text, image_size, text_name):
    save_path = '/tmp'
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    max_char_count = 40
    text_color = (255, 255, 255, 255)

    img = Image.new('RGBA', image_size, color=(190, 190, 190, 0))
    font = ImageFont.truetype(font=f'Dosis-Bold.ttf', size=50)
    draw = ImageDraw.Draw(im=img)
    avg_char_width = sum(font.getbbox(char)[2] for char in ascii_letters) / len(ascii_letters)
    max_char_count = max(int(img.size[0] * .718 / avg_char_width), max_char_count)
    new_text = textwrap.fill(text=text, width=max_char_count, replace_whitespace=False)
    shadow_image = Image.new('RGBA', img.size, color=(255, 255, 255, 0))
    shadow_draw = ImageDraw.Draw(im=shadow_image)
    shadow_draw.text(xy=(img.size[0] / 2 - 1, img.size[1] / 2 + 4), text=new_text, font=font, fill=(0, 0, 0, 80),
                     anchor='mm',
                     align='center')
    draw.text(xy=(img.size[0] / 2, img.size[1] / 2), text=new_text, font=font, fill=text_color, anchor='mm',
              align='center')
    combined = Image.alpha_composite(shadow_image, img)
    final = combined.crop(combined.getbbox())
    path_to_check = f"{save_path}/{text_name}.png"
    final.save(f"{path_to_check}")
    return f"{path_to_check}", combined.getbbox()[3] - combined.getbbox()[1]


def upload(video_path, caption):
    video_upload_data = {}
    try:
        ig_user_id = os.environ['ig_user_id']
        access_token = os.environ['ig_access_token']
        post_url = 'https://graph.facebook.com/v18.0/{}/media'.format(ig_user_id)
        video_upload_data = imgur.upload_video(video_path)
        if not video_upload_data:
            print("video hosting failed")
            return

        payload = {
            'video_url': video_upload_data['link'],
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
            content_generator.delete_row()
        else:
            print("Reel posting not possible")
    except Exception as e:
        print(e)
        communication.telegram_bot_sendtext("Reel failed to post to instagram : " + str(e))
    finally:
        os.remove(video_path)
        if 'deletehash' in video_upload_data:
            imgur.delete(video_upload_data['deletehash'])


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
