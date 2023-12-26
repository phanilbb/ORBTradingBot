import json

from openai import OpenAI
import gspread

client = OpenAI(api_key='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')

prompt = '''can u give me relationship quotes and captions in around 20-30 words respectively as a python list (just as a list) of dict with keys as "quote", "caption" for my instagram page. Plz use emojis in the end quotes and captions. Give me 10 results.
1. The quotes should be like Me saying to my girl friend or boy friend.
[ ]'''


def get_sheet():
    gc = gspread.service_account(filename='credentials.json')
    gsheet = gc.open_by_key("1m1Gm_TmilUNlsA_EfmoTDb5LGHj15qQqdjAX2vZbFzo")
    return gsheet.worksheet("upload")


def lambda_handler(event, context):
    sheet = get_sheet()
    print("Content sheet rows : {}".format(sheet.row_count))
    if sheet.row_count < 100:
        content = [
        ]

        # print("requesting open AI")
        # completion = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=[
        #         {"role": "system", "content": "You are a great writer"},
        #         {"role": "user", "content": prompt}
        #     ]
        # )
        # print("choices len : " + str(len(completion.choices)))
        # content = completion.choices[0].message.content
        # print(content)
        if isinstance(content, list):
            upload_to_sheet(content, sheet)
        else:
            upload_to_sheet(json.loads(content), sheet)


def upload_to_sheet(content, uploadSheet):
    print("uploading to sheet : " + str(len(content)))
    for each_content in content:
        data = []
        data.append(each_content['quote'])
        data.append(each_content['caption'])
        uploadSheet.append_row(data)
    print("Uploaded to sheet")
