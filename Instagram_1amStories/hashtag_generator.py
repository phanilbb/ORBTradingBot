import requests
import json
import communication
import twitter

hashtag_generator_url = "https://www.veed.io/script-generator-ap/api/generate-non-streaming-text"

default_hashtags = "#quotes #quoteoftheday #quotesdaily #quotesaboutlife"


def generate_hashtags(topic):
    payload = json.dumps({
        "topic": topic,
        "keywords": topic,
        "vibe": None,
        "format": None,
        "slug": "hashtag-generator",
        "number": 1
    })
    headers = {
        'authority': 'www.veed.io',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        'origin': 'https://www.veed.io',
        'referer': 'https://www.veed.io/tools/script-generator/hashtag-generator?utm_source=google&utm_medium=cpc&utm_campaign=Search_PerfomanceMax_Youtube_ROW_ENG_Speaking&utm_content=&utm_term=&gad_source=1&gclid=CjwKCAjwkY2qBhBDEiwAoQXK5Vw4bFaypydgYLfEdOw3LLs14vkwkU_D7ewGDrmP1PhGgEwG-CdD-RoCJ4YQAvD_BwE',
        'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }

    try:
        r = requests.post(hashtag_generator_url, data=payload, headers=headers)
        print("Hashtags : " + json.dumps(r.json()))
        return r.json()
    except Exception as e:
        print("Hashtag generation failed : " + str(e))
        communication.telegram_bot_sendtext("Hashtag generation failed : " + str(e))


def generate_hashtags_from_text(text, topic):
    try:
        hashtags = generate_hashtags(topic)
        twitter_hashtags = twitter.get_trending_hashtags()
        if hashtags:
            data = hashtags[0]
            data = data.replace('\n', ' ')
            data = data.replace('# ', '#')
            return get_hashtags(twitter_hashtags, data, default_hashtags)
        else:
            return get_hashtags(twitter_hashtags, '', default_hashtags)
    except Exception as e:
        print(e)
        return default_hashtags


def get_hashtags(twitter_hashtags, data, default_hashtags):
    result = default_hashtags.split('#')  + (' '.join(twitter_hashtags)).split('#') + data.split('#')
    result_updated = ['#' + each for each in result if each]
    if len(result_updated) > 28:
        result_updated = result_updated[0:28]

    return ' '.join(result_updated)


if __name__ == "__main__":
    text = "Love is not about how much you say 'I love you,' but how much you can prove that it's true."
    print(generate_hashtags_from_text(text), 'love')
