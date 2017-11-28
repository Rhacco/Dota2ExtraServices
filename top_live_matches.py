from utilities import log
import api
import top_recent_matches
import pro_players

data = []  # sorted by descending average MMR, tournament matches first
__data = {}  # for convenient internal use, unsorted

def fetch_new_matches():
    steam_result = []
    try:
        steam_result = api.dota2.get_top_live_games()['game_list']
    except Exception as e:
        log('Failed to fetch new matches: ' + str(e))
        return
    for steam_live_match in steam_result:
        server_id = int(steam_live_match['server_steam_id'])
        if server_id not in __data:
            realtime_stats = {}
            try:
                realtime_stats = api.dota2_get_realtime_stats(server_id)
            except Exception as e:
                log('Failed to fetch realtime stats for new match on %s: %s' %
                        (str(server_id), str(e)))
                continue
            match_id = int(realtime_stats['match']['matchid'])
            if match_id > 0 and match_id not in top_recent_matches.data:
                __data[server_id] = __convert(steam_live_match, realtime_stats)
                __insert_sorted(__data[server_id])

def update_realtime_stats():
    for server_id, live_match in __data.items():
        try:
            realtime_stats = api.dota2_get_realtime_stats(server_id)
            __set_realtime_stats(live_match, realtime_stats)
        except Exception as e:
            log('Failed to update realtime stats of %s: %s' %
                    (str(server_id), str(e)))

def remove(match_id):
    for index, live_match in enumerate(data):
        if match_id == live_match['match_id']:
            data.pop(index)
            break
    for server_id, live_match in __data.items():
        if match_id == live_match['match_id']:
            __data.pop(server_id)
            return
    raise ValueError('Match ID %s not registered' % str(match_id))

def __convert(steam_live_match, realtime_stats):  # only keep relevant data
    converted = {}
    converted['server_id'] = int(steam_live_match['server_steam_id'])
    converted['match_id'] = int(realtime_stats['match']['matchid'])
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
            steam_id = player['accountid']
            new_player = {}
            new_player['current_steam_name'] = player['name']
            new_player['steam_id'] = steam_id
            if steam_id in pro_players.data:
                pro = pro_players.data[steam_id]
                official_name = pro['name']
                if pro['team_tag']:  # if pro player is in a team currently
                    official_name = pro['team_tag'] + '.' + pro['name']
                new_player['official_name'] = official_name
            converted['players'].append(new_player)
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

def __insert_sorted(new_live_match):
    if new_live_match['is_tournament_match']:
        data.insert(0, new_live_match)
    else:
        for index, live_match in enumerate(data):
            if live_match['is_tournament_match']:
                continue
            if new_live_match['average_mmr'] > live_match['average_mmr']:
                data.insert(index, new_live_match)
                return
        data.append(new_live_match)
