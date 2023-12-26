from selenium import webdriver
from bs4 import BeautifulSoup
import time
from pinterest import PinterestImageScraper
from PIL import Image
import pytesseract
import os
import shutil
import json
import gspread

key = "love quotes"
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
directory_path = '/Users/labba.kumar/PycharmProjects/ORBTradingBot/scripts/{}/'.format(key)
chunk_size = 10
file_path = 'data.json'
ScrollNumber = 10


def get_sheet():
    gc = gspread.service_account(filename='credentials.json')
    gsheet = gc.open_by_key("1m1Gm_TmilUNlsA_EfmoTDb5LGHj15qQqdjAX2vZbFzo")
    return gsheet.worksheet("GPT Prompts")


def upload_to_sheet(contents, uploadSheet):
    print("uploading to sheet : " + str(len(contents)))
    for each_content in contents:
        uploadSheet.append_row([each_content])
    print("Uploaded to sheet")


def scrape_data(key):
    url = "https://in.pinterest.com/search/pins/?q={}&rs=typed".format(key)
    sleepTimer = 1

    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(options=options)  # path=r'to/chromedriver.exe'
    driver.get(url)

    data = []

    for _ in range(1, ScrollNumber):
        driver.execute_script("window.scrollTo(1,100000)")
        print("scrolling")
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        for link in soup.find_all('img'):
            if link.get('src') not in data:
                data.append(link.get('src'))
        time.sleep(sleepTimer)

    print("data found : {}".format(len(data)))
    return data


def download_data(data, key):
    p_scraper = PinterestImageScraper()
    p_scraper.download(data, key)


def get_already_processed_data(file_path):
    with open(file_path, 'r') as file:
        processed = json.load(file)

    return processed


def update_processed_data(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


def extract_text_from_image(image_path):
    # Open the image file
    image = Image.open(image_path)

    # Use pytesseract to do OCR on the image
    text = pytesseract.image_to_string(image)

    return text


def extract_text(directory_path):
    quotes = []

    count = 0
    # Loop through each file in the directory
    for filename in os.listdir(directory_path):

        if filename in processed:
            print("Skipping {} as its already exists".format(filename))
            continue

        if filename.endswith(('.jpg', '.jpeg', '.png')):

            count += 1
            # Construct the full path to the image file
            image_path = os.path.join(directory_path, filename)

            # Extract text from the current image
            extracted_text = extract_text_from_image(image_path)

            # Normalize the text to lowercase
            normalized_text = ' '.join(extracted_text.lower().replace('\n', ' ').split())

            if 5 < len(normalized_text) <= 300:
                quotes.append(normalized_text)

    print("data downloaded : {}".format(count))
    print("data retrieved : {}".format(len(quotes)))

    return quotes


def print_gpt_prompts(quotes):
    prompts = []
    for i in range(0, len(quotes), chunk_size):
        chunk = quotes[i:i + chunk_size]
        prompt = '''{quotes}
         
from each object in this list. I want you to do these things..

1. Extract the quote from each string of the list. Remove double quotes and authors name if its there. Mandatory add emoji to each quote and caption
2. Fix the sentence to a meaningful love quote or saying. 
3. If u cant fix the sentence then skip and move to next. 
4. I need a caption for each quote. and caption should have an emoji and caption should be of 5 to 10 words. 
5. I need the result in a python list of dict format with key 'quote'  and 'caption'.
'''
        prompts.append(prompt.format(quotes=chunk))

    if prompts:
        sheet = get_sheet()
        upload_to_sheet(prompts, sheet)


scraped_data = scrape_data(key)
download_data(scraped_data, key)
processed = get_already_processed_data(file_path)
quotes = extract_text(directory_path)
print_gpt_prompts(quotes)
filtered_list = [each.split('/')[-1] for each in scraped_data if each not in processed]
processed.extend(filtered_list)
update_processed_data(processed, file_path)
shutil.rmtree(directory_path)
