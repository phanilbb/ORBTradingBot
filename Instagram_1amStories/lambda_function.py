import upload

def lambda_handler(event, context):
    upload.new_post()
        