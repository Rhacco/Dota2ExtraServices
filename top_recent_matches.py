import api
import top_live_matches

import datetime
from copy import deepcopy

data = []
match_ids = []
__finished_live_matches = []
__expiration_dates = []  # compensate for two-minute delay of Steam Web API

def fetch_finished_matches():
    index = 0
    while index < len(top_live_matches.data):
        match_id = top_live_matches.match_ids[index]
        if match_id not in match_ids:
            try:
                # If this succeeds, match is finished
                steam_finished_match = api.dota2.get_match_details(match_id)
                __finished_live_matches.append(
                        (top_live_matches.data[index], steam_finished_match))
                now = datetime.datetime.now()
                expiration_date = now + datetime.timedelta(minutes=2)
                __expiration_dates.append(expiration_date)
                match_ids.insert(0, match_id)
            except Exception as e:
                if str(e) != '\'Match ID not found\'':
                    print('Failed to fetch a finished match: ' + str(e))
        index += 1

def handle_finished_matches():
    now = datetime.datetime.now()
    to_remove_self = []
    for index, expiration_date in enumerate(__expiration_dates):
        if now > expiration_date:
            live_match = __finished_live_matches[index][0]
            steam_finished_match = __finished_live_matches[index][1]
            try:
                match_id = steam_finished_match['match_id']
                top_live_matches.remove(match_id)
                data.insert(0, __convert(live_match, steam_finished_match))
                to_remove_self.append(index)
            except Exception as e:
                print('Failed to handle a finished match: ' + str(e))
    index = 0
    while index < len(to_remove_self):
        __finished_live_matches.pop(to_remove_self[index] - index)
        __expiration_dates.pop(to_remove_self[index] - index)
        index += 1
    while len(data) > 20:  # only keep most recent top matches
        data.pop()
        match_ids.pop()

def __convert(live_match, steam_finished_match):
    converted = deepcopy(live_match)
    converted.pop('server_id')
    converted.pop('elapsed_time')
    converted['radiant_score'] = steam_finished_match['radiant_score']
    converted['dire_score'] = steam_finished_match['dire_score']
    realtime_stats = api.dota2_get_realtime_stats(live_match['server_id'])
    converted['gold_advantage'] = realtime_stats['graph_data']['graph_gold'][-1]
    converted['duration'] = steam_finished_match['duration']
    converted['radiant_win'] = steam_finished_match['radiant_win']
    return converted
