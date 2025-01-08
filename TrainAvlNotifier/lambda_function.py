import requests
import communication

HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,hi;q=0.7',
    'if-none-match': 'W/"137ad-oF0VditPlwvZTBDAzj9+nyc8va0"',
    'origin': 'https://www.makemytrip.com',
    'priority': 'u=1, i',
    'referer': 'https://www.makemytrip.com/',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'Cookie': '_abck=178CA0BA2300677A7105726E60E0BFC7~-1~YAAQmFstFyBPYzaTAQAAmBKqqQ3q8+pD3QnhIXcI5P0LZ2/xrMDVc38SYSd/fD8uxS4Z4RXMHKKd/otOLkZLQCqUAG+mZSFAU47O5BJigG9N9ajKpGA13ALcOeCAqKentbNhcyR+xbWG28VvDcM3C+CbPTYyHrJWvchhUtrgU+L/VaN08rt5q9/e1i2nx7rVOD+xXbvlbcZlq+Px5QgNDwvQWcJ2Q8tBpKJJAf21yS2ZvNbaldQa0xwA+CsK5FRGYlQkn/E2db8U6wZRn4Rs+jDITGhXhEN0ld2giHaCZLsELl0+EtVEsgG5EqbcpkCHV6fPIhAEYdev/iXzVhShgT5gpx2C3dFR6Y0zmIxlynELvRy8TLAABNxoRQRNFwnyfKPs4tu3afyVi+XuTiRaRRS5jKLHgmQewBmSCjnU61VziUBJOm+T2Ke5imqsI7w=~-1~-1~-1; ak_bmsc=3E359F79DFF4E04C96C9B51F302FFDB5~000000000000000000000000000000~YAAQmFstFyFPYzaTAQAAmBKqqRrIcMiAVeUXTmV9je4eKLWsrlkDwGHcJHgmnnJHIy+d8gkUntEQFHsjfyoUtsK74m/JS7ahdpR/GTJLdBRFF5tVUeVA3RWQO45eTPPPqG72ZmI2zOfLsCro0Nklwiooq9AA6bfYv+j5aLRlnHftNFT0E0YhgEDiYygQNc7ZLEwqpHiwrEHA28mM5eXjJhJXIjg91L5QUkL2g7U/4QiKczDLC94RSgHwX2gGaxPO7xr9CjfL6SPFRBzb/moPv/qSGeIDmXYvmmHxBdBGnDPxReXhevIBQst9i78KmS+irk1eEvu6JaJEBKILLebjOz4+p+KyEwIxdmF1fJebjcly; bm_sv=699971C5359035A86506825C809675A5~YAAQiFstF3cecDOTAQAA/EKsqRqLx0EXpjZRkD4sR03bnt3LM1P/uCXi1nA9Had40bzWuizYUTxAePLtPw7cf+GVe2TBAkOd2S5gVqp1d/z0nTn1067oFYqY0HWEHFjIdYbnxmGlQKqvDiI0o+A0oVbh5wHexXlHGXRoVtXiSyUCKeLV7UX0CCxdjzqexu/h6Fxvq5nT3a8lJpVFoNuaH5azdOH+NbFSujymVbpRiHz8wSg4i3OT2zjBLxUC9a4j5xVnfw==~1; bm_sz=36B2957FBBE77FBC7A0578C3254A4550~YAAQmFstFyJPYzaTAQAAmBKqqRpH7qkH2vV2MkWBeQs+s0hmYVaiUG8ksv8vksHQqhPGQsj4/4RnXYa3pU8jlP710/SpGHNqPa3JvUrdiedMhEd1MwdWxC0e2le0U5AUTPs7FCNlXzJ2mFs028RAN3NNKDIBYVW6Tj4sZV12rSoyUwkeKQZw/Mo32oYK66AkM2aZZWpGziIYUvxbYdG0nIvw9gD4rC1i6Xuj/hL6Yfso21P1xVVxk1tJFYMzPD/anP5cPXpXXcvqfqA4Xr0jW/HJh1JsE6RTgJtWpzRN/VbcZNaT86wDJ2NiSxfitjv4j7b5WDxA7phky2dkO4BKbdUenZsduvPGulATBAn/lCC/HHg=~3555638~3354678'
}

URL = "https://railways.makemytrip.com/api/tbsWithAvailabilityAndRecommendation/SC/VSKP/20250111"


def lambda_handler(event, context):
    com = communication.Communication()
    try:
        r = requests.get(url=URL, headers=HEADERS)
        if r.status_code != 200:
            com.send_telegram_msg("Request Failed with status " + str(r.status_code))

        res_json = r.json()

        for each_train in res_json['trainBtwnStnsList']:
            for each_class in each_train['tbsAvailability']:
                status = each_class["availablityStatus"].lower()
                if 'available' in status or 'curr' in status:
                    com.send_telegram_msg("Availability found")
                    return

    except Exception as e:
        com.send_telegram_msg("Request Failed with exception " + str(e))
