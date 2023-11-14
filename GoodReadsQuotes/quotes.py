import requests
from bs4 import BeautifulSoup


def scrape(tag, page):
    quotes = []
    authors = []
    url = 'https://www.goodreads.com/quotes/tag/{}?page={}'.format(tag, page)
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        quote_elements = soup.find_all('div', class_='quoteText')
        for quote_element in quote_elements:
            quote_text = quote_element.text.strip()
            lines = quote_text.split('\n')
            quote = lines[0].strip().replace("“", '').replace("”", '')
            if len(quote.split()) <= 40:
                author = lines[4].strip()
                quotes.append(quote)
                authors.append(author)
    else:
        print(f"Error: Unable to fetch the page. Status code: {response.status_code}")

    return quotes, authors
