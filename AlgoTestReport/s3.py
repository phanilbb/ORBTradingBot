import boto3
from communication import Communication
from botocore.exceptions import NoCredentialsError


class S3:
    bucket = '1amstoriess'
    s3 = None
    url = 'https://1amstoriess.s3.ap-south-1.amazonaws.com'
    comm = None

    def __init__(self):
        self.comm = Communication()
        try:
            self.s3 = boto3.client('s3')
        except Exception as e:
            print("S3 connection failed with error : " + str(e))
            self.comm.send_telegram_msg("S3 connection failed with error : " + str(e))

    def get_images(self):
        response = self.s3.list_objects_v2(Bucket=self.bucket)
        return response

    def upload_file(self, path):
        try:
            self.s3.upload_file(path, self.bucket, path)
            print(f"File uploaded successfully to " + path)
        except FileNotFoundError:
            print(f"The file {path} was not found.")
            self.comm.send_telegram_msg(f"The file {path} was not found.")
        except NoCredentialsError:
            print("Credentials not available.")
            self.comm.send_telegram_msg("Credentials not available.")

    def delete_file(self, path):
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=path)
            print(f"File deleted successfully from {self.bucket}/{path}")
        except Exception as e:
            print("File Deletion Failed for key {} with error {} ".format(path, str(e)))
            self.comm.send_telegram_msg("File Deletion Failed for key {} with error {} ".format(path, str(e)))

    def get_public_url(self, path):
        return "{}/{}".format(self.url, path)
