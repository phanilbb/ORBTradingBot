import time

from GoodReadsQuotes import quotes
import gspread


def upload(quotes, authors, topic):
    gc = gspread.service_account(filename='credentials.json')
    gsheet = gc.open_by_key("1m1Gm_TmilUNlsA_EfmoTDb5LGHj15qQqdjAX2vZbFzo")
    uploadSheet = gsheet.worksheet("goodreads")

    for i in range(0, len(quotes)):
        data = []
        data.append(quotes[i])
        data.append(topic)
        data.append(authors[i])
        uploadSheet.append_row(data, 2)


if __name__ == '__main__':

    topics = ["inspirational-quotes", "life-lessons", "success", "time", "motivation", "truth", "happiness",
              "relationships", "breakup", "knowledge", "death", "faith", "failure"]

    for each_topic in topics:
        for i in range(1, 10):
            print("Fetching quotes for topic {} for page {}".format(each_topic, str(i)))
            quote_list, authors = quotes.scrape(each_topic, i)
            print("Uploading to sheeting : " + str(len(quote_list)))
            upload(quote_list, authors, each_topic.split("-")[0])
            print("Uploaded to sheet")
            time.sleep(60)