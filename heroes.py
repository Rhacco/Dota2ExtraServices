import api

from collections import OrderedDict

data = {}

def fetch():
    global data
    steam_result = api.dota2.get_heroes()  # note: also provides all portraits!
    for hero in steam_result['heroes']:
        data[int(hero['id'])] = hero['localized_name']
    data = OrderedDict(sorted(data.items()))
