import os
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
import random
import s3


def get_audio_file():
    audio_list = s3.get_audio_list()
    if not audio_list:
        print("No audio files found in the specified folder.")
        return None
    random_audio_file = random.choice(audio_list)
    return s3.download_file(random_audio_file, '/tmp', 'downloaded_audio.mp3')


def get_video():
    video_list = s3.get_video_list()
    if not video_list:
        print("No video files found in the specified folder.")
        return None
    file = random.choice(video_list)

    return s3.download_file(file, '/tmp', 'downloaded_file.mp4')


def create_video(text, text_name, video_file, audio_file, file_name):
    image_text_source_y = 700
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height', '-of', 'csv=p=0:s=x', video_file],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    video_size = re.findall('\d+', result.stdout.decode())[0:2]
    video_width, video_height = map(int, video_size)

    ffprobe_command = f'ffprobe -i "{video_file}" -show_entries format=duration -v quiet -of csv="p=0"'
    video_duration = subprocess.check_output(ffprobe_command, shell=True)
    video_duration = float(video_duration.decode('utf-8').strip())

    text_start_time = 0
    created_verse_image_data = create_image(text, (int(video_width), int(video_height)), text_name)
    created_verse_image = created_verse_image_data[0]

    text2_y: int = image_text_source_y

    output_path = '/tmp'
    if output_path:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        output_path = output_path + "/{}.mp4".format(file_name)
    else:
        output_path = "{}.mp4".format(file_name)

    if os.environ.get("env", "aws") == "local":
        output_path = "{}.mp4".format(file_name)

    ffmpeg_command = (
        'ffmpeg -loglevel error -stats -y -i "{}" '
        '-i "{}" -i "{}" -r 24 -filter_complex '
        '"[1:v]eq=brightness=-0.1[g];[g]gblur=sigma=10[v1]; '
        '[v1][2:v]overlay=(W-w)/2:{}:enable=\'between(t,{},{})\'[v2]" '
        '-t {} -map "[v2]" -map 0 -c:v libx264 -preset veryfast -crf 18 -s 1080x1920 "{}"'
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

    max_char_count = 35
    text_color = (255, 255, 255, 255)

    img = Image.new('RGBA', image_size, color=(190, 190, 190, 0))
    font = ImageFont.truetype(font=f'Dosis-Bold.ttf', size=70)
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
            content_generator.delete_row()
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
