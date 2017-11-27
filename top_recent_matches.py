from utilities import log
import api
import top_live_matches

from collections import OrderedDict
import datetime
from copy import deepcopy

data = OrderedDict()  # sorted by time finished, most recent first
__finished_live_matches = {}
__expiration_dates = {}  # compensate for two-minute delay of Steam Web API

def fetch_finished_matches():
    for live_match in top_live_matches.data:
        match_id = live_match['match_id']
        if match_id not in __finished_live_matches:
            try:
                # If this succeeds, match is finished
                steam_finished_match = api.dota2.get_match_details(match_id)
                __finished_live_matches[match_id] = (live_match,
                                                     steam_finished_match)
                now = datetime.datetime.now()
                expiration_date = now + datetime.timedelta(minutes=2)
                __expiration_dates[match_id] = expiration_date
            except Exception as e:
                if str(e) != '\'Match ID not found\'':
                    log('Failed to fetch finished match %d: %s' %
                            (match_id, str(e)))

def handle_finished_matches():
    now = datetime.datetime.now()
    to_remove_self = []
    for match_id, expiration_date in __expiration_dates.items():
        if now > expiration_date:
            live_match = __finished_live_matches[match_id][0]
            steam_finished_match = __finished_live_matches[match_id][1]
            try:
                top_live_matches.remove(match_id)
                data[match_id] = __convert(live_match, steam_finished_match)
                data.move_to_end(match_id, last=False)  # needs Python 3.2+!
                to_remove_self.append(match_id)
            except Exception as e:
                log('Failed to handle finished match %d: %s' %
                        (match_id, str(e)))
    for match_id in to_remove_self:
        __finished_live_matches.pop(match_id)
        __expiration_dates.pop(match_id)
    while len(data) > 20:  # only keep most recent top matches
        data.popitem()

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
