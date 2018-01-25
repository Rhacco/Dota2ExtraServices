import api
import top_recent_matches
import pro_players

data = []  # sorted by descending average MMR, tournament matches first
_data = {}  # for convenient internal use, unsorted
fail_counters = {}  # compensate for corrupt API calls occurring sometimes

def fetch_new_matches():
    steam_result = []
    try:
        steam_result = api.dota2.get_top_live_games()['game_list']
    except:
        return
    for steam_live_match in steam_result:
        server_id = int(steam_live_match['server_steam_id'])
        if server_id in _data:
            try:
                live_match = _data[server_id]
                live_match['spectators'] = steam_live_match['spectators']
            except:
                pass
        else:
            try:
                realtime_stats = api.dota2_get_realtime_stats(server_id)
                match_id = int(realtime_stats['match']['matchid'])
                if match_id not in top_recent_matches.data and match_id > 0:
                    converted = _convert(steam_live_match, realtime_stats)
                    _data[server_id] = converted
                    _insert_sorted(converted)
            except:
                pass

def update_realtime_stats():
    to_remove = []
    for server_id, live_match in _data.items():
        try:
            realtime_stats = api.dota2_get_realtime_stats(server_id)
            set_realtime_stats(live_match, realtime_stats)
        except:
            match_id = live_match['match_id']
            if match_id not in fail_counters:
                fail_counters[match_id] = 0
            fail_counters[match_id] += 1
            if fail_counters[match_id] >= 10:
                to_remove.append(match_id)
    for match_id in to_remove:
        remove(match_id)
        fail_counters.pop(match_id)

def remove(match_id):
    for index, live_match in enumerate(data):
        if match_id == live_match['match_id']:
            data.pop(index)
            break
    for server_id, live_match in _data.items():
        if match_id == live_match['match_id']:
            _data.pop(server_id)
            return

def _convert(steam_live_match, realtime_stats):  # only keep relevant data
    converted = {}
    converted['server_id'] = int(steam_live_match['server_steam_id'])
    converted['match_id'] = int(realtime_stats['match']['matchid'])
    converted['delay'] = steam_live_match['delay']
    converted['spectators'] = steam_live_match['spectators']
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
                pro_data = pro_players.data[steam_id]
                official_name = pro_data['name']
                if pro_data['team_tag']:  # if pro player is in a team currently
                    official_name = pro_data['team_tag'] + '.' + official_name
                new_player['official_name'] = official_name
                if converted['is_tournament_match']:
                    new_player.pop('current_steam_name')
            converted['players'].append(new_player)
    set_realtime_stats(converted, realtime_stats)
    return converted

def set_realtime_stats(live_match, realtime_stats):
    live_match['radiant_score'] = realtime_stats['teams'][0]['score']
    live_match['dire_score'] = realtime_stats['teams'][1]['score']
    gold_advantage = realtime_stats['graph_data']['graph_gold'][-1]
    elapsed_time = max(0, realtime_stats['match']['game_time'])
    live_match['gold_advantage'] = gold_advantage
    live_match['elapsed_time'] = elapsed_time
    players = realtime_stats['teams'][0]['players']
    players.extend(realtime_stats['teams'][1]['players'])
    for index, player in enumerate(players):
        score_kda = '%s/%s/%s' % (str(player['kill_count']),
            str(player['death_count']), str(player['assists_count']))
        live_match['players'][index]['score_kda'] = score_kda
    if 'heroes' in live_match:
        return  # all heroes are already assigned, nothing more to do
    heroes = []
    for player in players:
        heroes.append(player['heroid'])
    if len(heroes) == 10 and heroes[9] > 0:  # if all heroes are assigned
        live_match['heroes'] = heroes
    else:
        live_match['gold_advantage'] = 0
        live_match['elapsed_time'] = 0

def _insert_sorted(new_live_match):
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
