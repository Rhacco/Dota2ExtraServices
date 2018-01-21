from config import API_KEY

import dota2api
import urllib
import json

dota2 = dota2api.Initialise(API_KEY)

def dota2_get_realtime_stats(server_id):
    url = ('https://api.steampowered.com/IDOTA2MatchStats_570/GetRealtimeStats/'
           'v1/?key=%s&server_steam_id=%s' % (str(API_KEY), str(server_id)))
    return __fetch(url)

def dota2_get_leaderboard(region):
    url = ('http://www.dota2.com/webapi/ILeaderboard/GetDivisionLeaderboard/'
            'v0001?division=%s' % region)
    return __fetch(url)['leaderboard']

def opendota_get_pro_players():
    return __fetch('https://api.opendota.com/api/proPlayers')

def __fetch(url):
    data = urllib.request.urlopen(url).read().decode()  # needs Python 3+!
    data = json.loads(data)
    return data
