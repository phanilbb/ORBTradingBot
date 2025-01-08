import time
import urllib.request
import bs4
from communication import Communication

LINKS = [
    {
        "url": "https://www.amazon.in/Samsung-inches-Crystal-Vivid-UA75DUE77AKXXL/dp/B0CX5FY89F",
        "price": 70000,
        "product": "Samsung TV 75 inches"
    },
    {
        "url": "https://www.amazon.in/Xiaomi-inches-Ultra-Google-L65M8-A2IN/dp/B0CH31ZLNQ",
        "price": 40000,
        "product": "Xiaomi TV 65 inches"
    },
    {
        "url": "https://www.amazon.in/Haier-Inverter-Refrigerator-HES-690IM-P-Convertible/dp/B0BZ135HFX",
        "price": 50000,
        "product": "Haier Fridge"
    },
    {
        "url": "https://www.amazon.in/ILIFE-T20s-Self-Emptying-Navigation-Simultaneous/dp/B0BTTDLW7L",
        "price": 20000,
        "product": "ILIFE Robo Vaccum Cleaner"
    },
    {
        "url": "https://www.amazon.in/Panasonic-Condenser-Convertible-CS-CU-NU18ZKY5W/dp/B0CSCWVKGK",
        "price": 35000,
        "product": "Panasonic AC"
    },
    {
        "url": "https://www.amazon.in/Bosch-Settings-Dishwasher-SMS66GI01I-Silver/dp/B07JW58P2C",
        "price": 33000,
        "product": "Bosch Dishwasher"
    }
]

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
    for each_link in LINKS:
        comm = Communication()
        try:
            req = urllib.request.Request(each_link['url'], headers=HEADERS)
            response = urllib.request.urlopen(req)
            sauce = response.read()
            soup = bs4.BeautifulSoup(sauce, "html.parser")
            try:
                price = float(soup.find(class_="a-offscreen").get_text().replace("₹", "").replace(",", ""))
            except AttributeError():
                price = float(soup.find(class_="a-price-whole").get_text().replace(",", "").replace(".", ""))

            if not price:
                comm.send_telegram_msg("Price Not found for : " + each_link['product'])
            elif price < each_link['price']:
                comm.send_telegram_msg("Price Drop alert for : " + each_link['url'])
            else:
                print("Product not within buy range for : " + each_link['product'])
        except Exception as e:
            comm.send_telegram_msg("Exception " + str(e) + " for product " + each_link['product'])

        time.sleep(10)
