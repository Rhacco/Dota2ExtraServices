from utilities import list_to_string
from utilities import make_camel_case

import json
import api
import re

data = []

def update():
    items = json.load(open('node_modules/dotaconstants/build/items.json'))
    data_by_item_id = {}
    for _, item in items.items():
        if _insert_sorted(_convert(item)):
            data_by_item_id[item['id']] = item
    steam_items = api.dota2.get_game_items()
    for item in steam_items['items']:
        if item['id'] not in data_by_item_id:
            continue
        data_by_item_id[item['id']]['is_recipe'] = item['recipe'] == 1
        data_by_item_id[item['id']]['in_secret_shop'] = item['secret_shop'] == 1
        data_by_item_id[item['id']]['in_side_shop'] = item['side_shop'] == 1

def _convert(item):
    if 'dname' not in item:
        return item
    item['desc'] = _fix_spaces(item['desc'])
    item['notes'] = _fix_spaces(item['notes'])
    for attrib in item['attrib']:
        converted = make_camel_case(attrib['header'].replace('\\n', ''))
        attrib['header'] = converted.replace('Hp', 'HP')
        if isinstance(attrib['value'], list):
            attrib['value'] = list_to_string(attrib['value'], ' / ')
    if item['dname'] == 'Boots of Travel':
        if item['id'] == 48:
            item['dname'] += ' 1'
        else:
            item['dname'] += ' 2'
    elif item['dname'] == 'Dagon':
        if item['id'] == 104:
            item['dname'] += ' 1'
        elif item['id'] == 201:
            item['dname'] += ' 2'
        elif item['id'] == 202:
            item['dname'] += ' 3'
        elif item['id'] == 203:
            item['dname'] += ' 4'
        else:
            item['dname'] += ' 5'
    elif item['dname'] == 'Diffusal Blade':
        if item['id'] == 174:
            item['dname'] += ' 1'
        else:
            item['dname'] += ' 2'
    elif item['dname'] == 'Necronomicon':
        if item['id'] == 106:
            item['dname'] += ' 1'
        elif item['id'] == 193:
            item['dname'] += ' 2'
        else:
            item['dname'] += ' 3'
    return item

def _fix_spaces(string):
    string = string.replace('  ', ' ')
    return re.sub(r'([.|a-z|0-9])([A-Z])', r'\1 \2', string)

def _insert_sorted(new_item):
    if 'dname' not in new_item:
        return False
    if new_item['dname'].startswith('River Vial'):
        return False
    for index, item in enumerate(data):
        if new_item['dname'] == item['dname']:
            print('\n!!! Need to convert !!!\n\n', new_item)
        if new_item['dname'] < item['dname']:
            data.insert(index, new_item)
            return True
    data.append(new_item)
