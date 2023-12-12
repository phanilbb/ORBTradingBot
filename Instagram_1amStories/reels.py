import os
import random
import re
import subprocess
import sys
import time

from PIL import Image
from helpers import constants
import image_editor
import s3


def get_audio_file(topic):
    audio_list = s3.get_audio_list(topic)
    if not audio_list:
        audio_list = s3.get_audio_list("default")
    if not audio_list:
        print("No audio files found in the specified folder.")
        return None
    random_audio_file = random.choice(audio_list)
    return s3.download_file(random_audio_file, '/tmp', '{}.mp3'.format(str(round(time.time() * 1000))))


def get_video():
    video_list = s3.get_video_list()
    if not video_list:
        print("No video files found in the specified folder.")
        return None
    file = random.choice(video_list)

    return s3.download_file(file, '/tmp', '{}.mp4'.format(str(round(time.time() * 1000))))


def create_video(content, text_name, video_file, audio_file, file_name):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height', '-of', 'csv=p=0:s=x', video_file],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    video_size = re.findall('\d+', result.stdout.decode())[0:2]
    video_width, video_height = map(int, video_size)

    ffprobe_command = f'ffprobe -i "{video_file}" -show_entries format=duration -v quiet -of csv="p=0"'
    video_duration = subprocess.check_output(ffprobe_command, shell=True)
    video_duration = float(video_duration.decode('utf-8').strip())

    question_image = create_image(content['Title'], (int(video_width), int(video_height)), text_name + "title")
    answers_image = create_image(content['Content'], (int(video_width), int(video_height)), text_name + "content")

    output_path = '/tmp'
    if output_path:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        output_path = output_path + "/{}.mp4".format(file_name)
    else:
        output_path = "{}.mp4".format(file_name)

    if os.environ.get("env", "aws") == "local":
        output_path = "{}.mp4".format(file_name)

    text_start_time = 0
    text_height = 0

    ffmpeg_command = (
        'ffmpeg -loglevel error -stats -y -i "{}" '
        '-i "{}" -i "{}" -i "{}" -i "{}" -r 24 -filter_complex '
        '"[1:v]eq=brightness=-0.1[g];[g]gblur=sigma=10[v1]; '
        '[v1][2:v]overlay=(W-w)/2:{}:enable=\'between(t,{},{})\'[v2]; '
        '[v2]overlay=(W-w)/2:{}:enable=\'between(t,{},{})\'[v3]; '
        '[v3]overlay=(W-w)/2:{}:enable=\'between(t,{},{})\'[v4]" '
        '-t {} -map "[v4]" -map 0 -c:v libx264 -preset veryfast -crf 18 -s 1080x1920 "{}"'
    ).format(
        audio_file, video_file, question_image, answers_image, answers_image,
        text_height, text_start_time, text_start_time + 2,
        text_height, text_start_time + 3, video_duration - 3,
        text_height, video_duration - 3, video_duration,
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


def create_image(text, img_size, text_name):
    save_path = '/tmp'
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    text_color = (255, 255, 255)
    data = {
        'Title': text
    }
    img = Image.new('RGBA', img_size, color=(190, 190, 190, 0))
    image_editor.add_main_text(img, data, text_color, text_width=constants.TEXT_WIDTH_REEL)
    path_to_check = f"{save_path}/{text_name}.png"
    img.save(f"{path_to_check}")
    return path_to_check
