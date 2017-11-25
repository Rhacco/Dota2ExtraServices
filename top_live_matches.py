from utilities import log
import api
import top_recent_matches

server_ids = []
match_ids = []
data = []

def update():
    steam_result = []
    try:
        steam_result = api.dota2.get_top_live_games()['game_list']
    except:
        log('Failed to fetch top live matches')
        return
    for live_match in steam_result:
        server_id = live_match['server_steam_id']
        if server_id not in server_ids:
            if server_id not in top_recent_matches.server_ids:
                rt_stats = api.dota2_get_realtime_stats(server_id)
                if rt_stats is None:
                    log('Failed to fetch realtime stats')
                else:
                    try:
                        match_ids.append(rt_stats['match']['matchid'])
                        server_ids.append(server_id)
                        data.append(live_match)
                    except:
                        log('Failed to fetch match ID')

def remove(index):
    server_ids.pop(index)
    match_ids.pop(index)
    data.pop(index)

#def __convert(live_match, realtime_stats):
    # TODO
