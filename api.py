from config import API_KEY

import dota2api
import urllib
import json

dota2 = dota2api.Initialise(API_KEY)

def dota2_get_realtime_stats(server_id):
    url = ('https://api.steampowered.com/IDOTA2MatchStats_570/GetRealtimeStats/'
           'v1/?key={}&server_steam_id={}').format(API_KEY, server_id)
    data = urllib.request.urlopen(url).read().decode()  # needs Python 3+!
    data = json.loads(data)
    return data
