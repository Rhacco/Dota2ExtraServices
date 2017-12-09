from utilities import log
import api
import top_live_matches

from collections import OrderedDict
import datetime
from copy import deepcopy

data = OrderedDict()  # sorted by time finished, most recent first
__finished_matches = {}  # queue of finished matches
__expiration_dates = {}  # compensate for the delay of the Steam Web API
__fail_counters = {}  # compensate for corrupt API calls occurring sometimes

def fetch_finished_matches():
    for live_match in top_live_matches.data:
        match_id = int(live_match['match_id'])
        if match_id not in __finished_matches:
            try:
                # If this succeeds, match is finished
                steam_finished_match = api.dota2.get_match_details(match_id)
                __finished_matches[match_id] = (live_match,
                                                steam_finished_match)
                now = datetime.datetime.now()
                delay = live_match['delay']
                expiration_date = now + datetime.timedelta(seconds=delay)
                __expiration_dates[match_id] = expiration_date
            except:
                pass

def handle_finished_matches():
    now = datetime.datetime.now()
    to_remove_finished = []
    to_remove_failed = []
    for match_id, expiration_date in __expiration_dates.items():
        if now > expiration_date:
            live_match = __finished_matches[match_id][0]
            steam_finished_match = __finished_matches[match_id][1]
            try:
                data[match_id] = __convert(live_match, steam_finished_match)
                data.move_to_end(match_id, last=False)  # needs Python 3.2+!
                to_remove_finished.append(match_id)
            except:
                if match_id not in __fail_counters:
                    __fail_counters[match_id] = 0
                __fail_counters[match_id] += 1
                if __fail_counters[match_id] >= 10:
                    to_remove_failed.append(match_id)
    for match_id in to_remove_finished:
        top_live_matches.remove(match_id)
        __finished_matches.pop(match_id)
        __expiration_dates.pop(match_id)
        if match_id in __fail_counters:
            __fail_counters.pop(match_id)
        if match_id in top_live_matches.fail_counters:
            top_live_matches.fail_counters.pop(match_id)
    for match_id in to_remove_failed:
        top_live_matches.remove(match_id)
        __finished_matches.pop(match_id)
        __expiration_dates.pop(match_id)
        __fail_counters.pop(match_id)
        if match_id in top_live_matches.fail_counters:
            top_live_matches.fail_counters.pop(match_id)
    while len(data) > 20:  # only keep most recent top matches
        data.popitem()

def __convert(live_match, steam_finished_match):
    converted = deepcopy(live_match)
    realtime_stats = api.dota2_get_realtime_stats(live_match['server_id'])
    top_live_matches.set_realtime_stats(converted, realtime_stats)
    converted.pop('server_id')
    converted.pop('delay')
    converted.pop('spectators')
    converted.pop('elapsed_time')
    converted['duration'] = steam_finished_match['duration']
    converted['radiant_win'] = steam_finished_match['radiant_win']
    return converted
