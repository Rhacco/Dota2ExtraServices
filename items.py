from utilities import list_to_string
from utilities import make_camel_case

import json
import re
import time

data = []
last_update = 0
_removed_items = [71, 196]


def update():
    global last_update
    dotaconstants = 'node_modules/dotaconstants/build/'
    items = json.load(open(dotaconstants + 'items.json'))
    item_names = json.load(open(dotaconstants + 'item_ids.json'))
    data_by_item_name = {}
    for _, item in items.items():
        converted = _convert(item)
        if _insert_sorted(converted):
            data_by_item_name[item_names[str(item['id'])]] = converted
    for item in data:
        if item['components'] is None:
            continue
        components = []
        for component_name in item['components']:
            component = data_by_item_name[component_name]
            name_with_cost = component['dname']
            name_with_cost += ' (' + str(component['cost']) + ')'
            components.append(name_with_cost)
        recipe = _data_by_item_dname(item['dname'] + ' Recipe')
        if recipe:
            components.append('Recipe (' + str(recipe['cost']) + ')')
        item['components'] = list_to_string(components, ', ')
    last_update = time.time()


def _convert(item):
    if 'dname' not in item:
        return item
    for attrib in item['attrib']:
        converted = make_camel_case(attrib['header'].replace('\\n', ''))
        attrib['header'] = converted.replace('Hp', 'HP')
        if isinstance(attrib['value'], list):
            attrib['value'] = list_to_string(attrib['value'], ' / ')
    if isinstance(item['mc'], bool):
        item.pop('mc')
    if isinstance(item['cd'], bool):
        item.pop('cd')
    item['desc'] = _fix_spaces(item['desc'])
    item['desc'] = re.sub(r'[\n]{1,}', '\n\n', item['desc'])
    item['notes'] = _fix_spaces(item['notes'])
    item['notes'] = re.sub(r'[\n]{1,}', '\n\n', item['notes'])
    if item['dname'] == 'Cheese' or item['dname'] == 'Refresher Shard':
        item['cost'] = 0
    elif item['dname'] == 'Boots of Travel':
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
    elif item['dname'] == 'Necronomicon':
        if item['id'] == 106:
            item['dname'] += ' 1'
        elif item['id'] == 193:
            item['dname'] += ' 2'
        else:
            item['dname'] += ' 3'
    return item


def _fix_spaces(string):
    string = re.sub(r'[ ]{1,}', ' ', string)
    return re.sub(r'([.|a-z|0-9])([A-Z])', r'\1 \2', string)


def _insert_sorted(new_item):
    if 'dname' not in new_item or new_item['id'] in _removed_items:
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
    return True


def _data_by_item_dname(item_dname):
    for item in data:
        if item['dname'] == item_dname:
            return item
    return None
