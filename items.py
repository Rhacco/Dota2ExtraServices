import api

from collections import OrderedDict

data = {}

def fetch():
    global data
    steam_result = api.dota2.get_game_items()  # note: also provides portraits!
    for item in steam_result['items']:
        converted = {}
        converted['name'] = item['localized_name']
        converted['cost'] = item['cost']
        converted['recipe'] = item['recipe'] == 1
        converted['secret_shop'] = item['secret_shop'] == 1
        converted['side_shop'] = item['side_shop'] == 1
        data[int(item['id'])] = converted
    data = OrderedDict(sorted(data.items()))
