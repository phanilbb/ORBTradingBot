import boto3
import os
import communication
from botocore.exceptions import NoCredentialsError

BUCKET_NAME = '1amstoriess'
AUDIO_FOLDER = 'audio/'
IMAGE_FOLDER = 'images/'
VIDEO_FOLDER = 'videos/'
S3 = None

BASE_URL = 'https://1amstoriess.s3.ap-south-1.amazonaws.com'


def get_s3_connection():
    global S3
    if not S3:
        try:
            S3 = boto3.client('s3')
        except Exception as e:
            print("S3 connection failed with error : " + str(e))
            communication.telegram_bot_sendtext("S3 connection failed with error : " + str(e))
    return S3


def get_folder_objects(folder_path):
    s3 = get_s3_connection()
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=folder_path)
    return response


def download_file(file_path, local_directory, file_name):
    s3 = get_s3_connection()
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    local_path = local_directory + "/{}".format(file_name)
    s3.download_file(BUCKET_NAME, file_path, local_path)
    return local_path


def upload_file(local_file_path, s3_folder, s3_file_name):
    s3_folder = s3_folder.split('/')[1]
    s3 = get_s3_connection()
    s3Key = '{}/{}'.format(s3_folder, s3_file_name)
    try:
        s3.upload_file(local_file_path, BUCKET_NAME, s3Key)
        print(f"File uploaded successfully to " + s3Key)
    except FileNotFoundError:
        print(f"The file {local_file_path} was not found.")
        communication.telegram_bot_sendtext(f"The file {local_file_path} was not found.")
    except NoCredentialsError:
        print("Credentials not available.")
        communication.telegram_bot_sendtext("Credentials not available.")
    return s3_folder + "/" + s3_file_name


def delete_file(s3Key):
    s3 = get_s3_connection()
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=s3Key)
        print(f"File deleted successfully from {BUCKET_NAME}/{s3Key}")
    except Exception as e:
        print("File Deletion Failed for key {} with error {} ".format(s3Key, str(e)))
        communication.telegram_bot_sendtext("File Deletion Failed for key {} with error {} ".format(s3Key, str(e)))


def fetch_keys(response, ends_with):
    return [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith(ends_with)]


def get_images_list(topic):
    images_folder = IMAGE_FOLDER + topic.lower() + "/"
    response = get_folder_objects(images_folder)
    return fetch_keys(response, '.jpg') + fetch_keys(response, '.jpeg')


def get_audio_list(topic):
    audio_folder = AUDIO_FOLDER + topic.lower() + "/"
    response = get_folder_objects(audio_folder)
    return fetch_keys(response, '.mp3')


def get_video_list():
    response = get_folder_objects(VIDEO_FOLDER)
    return fetch_keys(response, '.mp4')


def get_public_url(s3Key):
    return "{}/{}".format(BASE_URL, s3Key)
