from openai import OpenAI
import gspread

client = OpenAI(api_key='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')

prompt = '''
Considering yourself as a poet and content generator. Can you give me 50 word short notes for my instagram page. I want to post sayings on below categories and need the content. Here is the requirement.
categories = ["love", "sad", "motivation", "breakup", "success", "failure"]
1. give me 12 results for the above categories - 3 on love category, 3 on breakup category,2 on success, 1 on failure, 1 on sad and 2 on motivation.
2. The content should be in 40-50 words and should be in simple English that a child human can understand and should be like a human-generated one. Please don't use heavy words. Please dont use questions in the content, it should be like a saying or expressing. Dont use hashtags in the conrent.
3. The content should have a title and then a description and use emojis. 
4. example for title "Why is he so special " "why i love her so much?", "Why I love u the most?" , "why is this happening only to me?"etc. The title should be a question..
5. The title should be a question.
6. I need a caption for the content (you can use emojis as well).
7. Give the response in a python list of dict format with keys "category", "title", "content", and "caption". I want only the title to be double quotes
8. you can generate the content considering the first person. like let's say you are writing a letter to a partner, you can consider yourself in the first person and write it to the partner. 
9. The content should be like a text with which either I'm communicating something to my followers or I'm conveying my feelings.
'''


def lambda_handler(event, context):
    print("requesting open AI")
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a poetic assistant, skilled in content generation, poems and sayings."},
            {"role": "user", "content": prompt}
        ]
    )
    print("choices len : " + str(len(completion.choices)))
    content = completion.choices[0].message.content
    print(content)
    upload_to_sheet(content)


def upload_to_sheet(content):
    gc = gspread.service_account(filename='credentials.json')
    gsheet = gc.open_by_key("1m1Gm_TmilUNlsA_EfmoTDb5LGHj15qQqdjAX2vZbFzo")
    uploadSheet = gsheet.worksheet("title_and_content")
    for each_content in content:
        data = []
        data.append(each_content['category'])
        data.append(each_content['title'])
        data.append(each_content['content'])
        data.append(each_content['caption'])
        uploadSheet.append_row(data)
    print("Uploaded to sheet")
