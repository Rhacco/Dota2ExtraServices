from utilities import log
import api
import top_recent_matches

data = {}

def fetch_new_matches():
    steam_result = []
    try:
        steam_result = api.dota2.get_top_live_games()['game_list']
    except Exception as e:
        log('Failed to fetch new matches: ' + str(e))
        return
    for steam_live_match in steam_result:
        server_id = int(steam_live_match['server_steam_id'])
        if server_id not in data:
            realtime_stats = {}
            try:
                realtime_stats = api.dota2_get_realtime_stats(server_id)
            except Exception as e:
                log('Failed to fetch realtime stats for new match on %d: %s' %
                        (server_id, str(e)))
                continue
            match_id = int(realtime_stats['match']['matchid'])
            if match_id > 0 and match_id not in top_recent_matches.data:
                data[server_id] = __convert(steam_live_match, realtime_stats)

def update_realtime_stats():
    for server_id, live_match in data.items():
        try:
            realtime_stats = api.dota2_get_realtime_stats(server_id)
            __set_realtime_stats(live_match, realtime_stats)
        except Exception as e:
            log('Failed to update realtime stats of %d: %s' %
                    (server_id, str(e)))

def remove(match_id):
    for server_id, live_match in data.items():
        if match_id == live_match['match_id']:
            data.pop(server_id)
            return
    raise ValueError('Match ID %d not registered' % match_id)

def __convert(steam_live_match, realtime_stats):  # only keep relevant data
    converted = {}
    converted['server_id'] = steam_live_match['server_steam_id']
    converted['match_id'] = realtime_stats['match']['matchid']
    average_mmr = steam_live_match['average_mmr']
    if average_mmr < 1:
        converted['is_tournament_match'] = True
        converted['team_radiant'] = steam_live_match['team_name_radiant']
        converted['team_dire'] = steam_live_match['team_name_dire']
    else:
        converted['is_tournament_match'] = False
        converted['average_mmr'] = average_mmr
    converted['players'] = []
    for team in realtime_stats['teams']:
        for player in team['players']:
            converted['players'].append(
                    {'current_steam_name': player['name'],
                     'steam_id': player['accountid']})
    __set_realtime_stats(converted, realtime_stats)
    return converted

def __set_realtime_stats(live_match, realtime_stats):
    live_match['radiant_score'] = realtime_stats['teams'][0]['score']
    live_match['dire_score'] = realtime_stats['teams'][1]['score']
    gold_advantage = realtime_stats['graph_data']['graph_gold'][-1]
    elapsed_time = max(0, realtime_stats['match']['game_time'])
    live_match['gold_advantage'] = gold_advantage
    live_match['elapsed_time'] = elapsed_time
    if 'heroes' in live_match:
        return  # heroes are already assigned, nothing more to do
    heroes = []
    for team in realtime_stats['teams']:
        for player in team['players']:
            heroes.append(player['heroid'])
    if (len(heroes) == 10 and heroes[0] > 0 and heroes[1] > 0):
        live_match['heroes'] = heroes
    else:  # heroes not assigned yet
        live_match['gold_advantage'] = 0
        live_match['elapsed_time'] = 0
