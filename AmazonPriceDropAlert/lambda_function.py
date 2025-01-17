import time
import urllib.request
import bs4
from communication import Communication

HEADERS = {
    'dnt': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://www.amazon.com/',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
}


def lambda_handler(event, context):
    for each_event in event:
        comm = Communication()
        try:
            req = urllib.request.Request(each_event['url'], headers=HEADERS)
            response = urllib.request.urlopen(req)
            sauce = response.read()
            soup = bs4.BeautifulSoup(sauce, "html.parser")
            try:
                price = float(soup.find(class_="a-offscreen").get_text().replace("₹", "").replace(",", ""))
            except AttributeError:
                price = float(soup.find(class_="a-price-whole").get_text().replace(",", "").replace(".", ""))

            if not price:
                comm.send_telegram_msg("Price Not found for : " + each_event['product'])
            elif price < each_event['price']:
                comm.send_telegram_msg("Price Drop alert for : " + each_event['url'])
            else:
                print("Product not within buy range for : " + each_event['product'])
        except Exception as e:
            comm.send_telegram_msg("Exception " + str(e) + " for product " + each_event['product'])

        time.sleep(10)
