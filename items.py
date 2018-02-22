import json
import api
import re

data = []

def update():
    items = json.load(open('node_modules/dotaconstants/build/items.json'))
    data_by_item_id = {}
    for _, item in items.items():
        item['desc'] = _fix_spaces(item['desc'])
        item['notes'] = _fix_spaces(item['notes'])
        if _insert_sorted(item):
            data_by_item_id[item['id']] = item
    steam_items = api.dota2.get_game_items()
    for item in steam_items['items']:
        if item['id'] not in data_by_item_id:
            continue
        data_by_item_id[item['id']]['is_recipe'] = item['recipe'] == 1
        data_by_item_id[item['id']]['in_secret_shop'] = item['secret_shop'] == 1
        data_by_item_id[item['id']]['in_side_shop'] = item['side_shop'] == 1

def _fix_spaces(description):
    description = description.replace('  ', ' ')
    return re.sub(r'([.|a-z|0-9])([A-Z])', r'\1 \2', description)

def _insert_sorted(new_item):
    if 'dname' not in new_item:
        return False
    for index, item in enumerate(data):
        if new_item['dname'] == item['dname']:
            if new_item['cost'] < item['cost']:
                data.insert(index, new_item)
                return True
        elif new_item['dname'] < item['dname']:
            data.insert(index, new_item)
            return True
    data.append(new_item)
