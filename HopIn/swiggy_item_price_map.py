import json

category_price_extra = {
    'Popsicle Waffle': 10,
    'Pan Cakes': 20,
    'Milk Shake / Thick Shake': 20,
    'Cold Beverages': 20
}


def get_items_response():
    file_path = 'items.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data['data']['menu']['items_vo']


def get_items_price_map():
    items = get_items_response()
    response = []
    for each_item in items:
        category = each_item['main_category_name']
        name = each_item['item']['name']
        price = float(each_item['item']['price'])
        response.append({
            'category': category,
            'name': name,
            'price': price,
            'shop_price': price - category_price_extra.get(category, 0)
        })
        if each_item['variant_groups_vo']:
            for each_variant_group in each_item['variant_groups_vo']:
                if each_variant_group['variants_vo']:
                    for each_variant in each_variant_group['variants_vo']:
                        response.append({
                            'category': category,
                            'name': "{} - {}".format(name, each_variant['variant']['name']),
                            'price': price + float(each_variant['variant']['price']),
                            'shop_price': price + float(each_variant['variant']['price']) - category_price_extra.get(category, 0)
                        })

    return response
