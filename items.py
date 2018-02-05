import json
import api

data = []

def update():
    items = json.load(open('node_modules/dotaconstants/build/' + 'items.json'))
    data_by_item_id = {}
    for _, item in items.items():
        data.append(item)
        data_by_item_id[item['id']] = item
    steam_items = api.dota2.get_game_items()  # note: also provides portraits!
    for item in steam_items['items']:
        if item['id'] not in data_by_item_id:
            continue
        data_by_item_id[item['id']]['is_recipe'] = item['recipe'] == 1
        data_by_item_id[item['id']]['in_secret_shop'] = item['secret_shop'] == 1
        data_by_item_id[item['id']]['in_side_shop'] = item['side_shop'] == 1
