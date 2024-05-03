import requests
from swiggy_item_price_map import get_items_price_map

WEEKLY_REPORT_TEMPLATE = '''WEEKLY Report - {}
<pre>
{}
</pre>
'''


def get_report(start_date: str, end_date: str) -> dict:
    url = "https://rms.swiggy.com/orders/v1/history?limit=50&offset=0&ordered_time__gte={}&ordered_time__lte={}&restaurant_id=867261".format(
        start_date, end_date)
    headers = {
        'Content-Type': 'application/json',
        'Origin': 'https://partner-self-client.swiggy.com',
        'Referer': 'https://partner-self-client.swiggy.com/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'accesstoken': '22456e39-c50e-4d15-a720-41e92b832f75'
    }

    response = requests.get(url, headers=headers)
    print(response.text)
    if response.status_code != 200:
        print("Swiggy report get failed")

    return response.json()


def get_items_quantity_map(response):
    items_quantity_map = {}
    items_price_map = {}
    data_list = response.get('data', [])
    for each_data in data_list:
        objects = each_data.get('data', {}).get('objects', [])
        for each_object in objects:
            items = each_object['cart']['items']
            for each_item in items:
                name = each_item['name']
                if not each_item['variants']:
                    if name in items_quantity_map:
                        items_quantity_map[name] += 1
                    else:
                        items_quantity_map[name] = 1
                for each_variant in each_item['variants']:
                    name_variant = "{} - {}".format(name, each_variant['name'])
                    if name_variant in items_quantity_map:
                        items_quantity_map[name_variant] += 1
                    else:
                        items_quantity_map[name_variant] = 1

    return items_quantity_map


def weekly_report(items_map):
    headers = ["Item", "Quantity", "Price", "Shop Price"]
    spaces = [60, 10, 10, 10]
    data = [["-" * spaces[0], '-' * spaces[1], '-' * spaces[2], '-' * spaces[3]]]
    items_price = get_items_price_map()
    sorted_dict = dict(sorted(items_map.items()))
    for key, value in sorted_dict.items():
        item_price_data = [e for e in items_price if e.get('name') == key]
        if not item_price_data:
            item_price_data = [{
                'price': 0,
                'shop_price': 0
            }]
        data.append([key, str(value), item_price_data[0]['price'], item_price_data[0]['shop_price']])

    table = create_table(headers, data, spaces)
    print(table)


def transform_to_characters(text, count):
    text = str(text)
    original_length = len(text)
    if original_length >= count:
        return text
    else:
        padding_length = (count - original_length) // 2
        padding = ' ' * padding_length
        padded_text = padding + text + padding
        if len(padded_text) < count:
            padded_text += ' '
        return padded_text


def create_table(headers, data, space_formats):
    # Initialize an empty string to store the table
    table = ''

    # Create the header row
    header_row = '|'.join([transform_to_characters(header, space_formats[i]) for i, header in enumerate(headers)])
    table += f"{header_row}|\n"

    # Create the separator row
    separator_row = '|'.join(
        [transform_to_characters('-' * space_formats[i], space_formats[i]) for i in range(len(headers))])
    table += f"{separator_row}|\n"

    # Create rows for each data entry
    for row_data in data:
        data_row = '|'.join([transform_to_characters(row_data[i], space_formats[i]) for i in range(len(headers))])
        table += f"{data_row}|\n"

    return table


def run():
    start_date = '2024-04-21'
    end_date = '2024-04-27'
    report = get_report(start_date, end_date)
    items_map = get_items_quantity_map(report)
    weekly_report(items_map)
