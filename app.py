from config import API_KEY
from flask import Flask, jsonify
import dota2api
import threading
import urllib
import json
import time

app = Flask(__name__)
api = dota2api.Initialise(API_KEY)

top_live_matches_server_ids = []
top_live_matches_match_ids = []
top_live_matches = []
top_recent_matches_server_ids = []
top_recent_matches = []

@app.route('/', methods=['GET'])
def get_index():
    return ('Additional Dota 2 services not directly available in the Steam Web'
            ' API. See https://github.com/Rhacco/Dota2ExtraServices')

@app.route('/TopLiveMatches', methods=['GET'])
def get_top_live_matches():
    return jsonify(top_live_matches)

@app.route('/TopRecentMatches', methods=['GET'])
def get_top_recent_matches():
    return jsonify(top_recent_matches)

def get_match_id(server_id):
    url = ('https://api.steampowered.com/IDOTA2MatchStats_570/GetRealtimeStats/'
           'v1/?key={}&server_steam_id={}').format(API_KEY, server_id)
    try:
        data = urllib.request.urlopen(url).read().decode()  # needs Python 3+!
        data = json.loads(data)
        match_id = data['match']['matchid']
        return match_id
    except:
        return None

def update_top_live_matches():
    steam_result = []
    try:
        steam_result = api.get_top_live_games()['game_list']
    except:
        print('Failed to fetch top live matches')
        return
    for match in steam_result:
        server_id = match['server_steam_id']
        if server_id not in top_live_matches_server_ids:
            if server_id not in top_recent_matches_server_ids:
                match_id = get_match_id(server_id)
                if match_id is None:
                    print('Failed to fetch match ID')
                else:
                    top_live_matches_server_ids.append(server_id)
                    top_live_matches_match_ids.append(match_id)
                    top_live_matches.append(match)

def update_top_recent_matches():
    to_remove = []
    index = 0
    while index < len(top_live_matches):
        try:
            # If this succeeds, match details are present and match is finished
            finished_top_match = api.get_match_details(
                    top_live_matches_match_ids[index])
            top_recent_matches_server_ids.insert(
                    0, top_live_matches_server_ids[index])
            top_recent_matches.insert(0, finished_top_match)
            to_remove.append(index)
        except:
            pass
        index += 1
    index = 0
    while index < len(to_remove):
            top_live_matches_server_ids.pop(to_remove[index] - index)
            top_live_matches_match_ids.pop(to_remove[index] - index)
            top_live_matches.pop(to_remove[index] - index)
            index += 1
    while (len(top_recent_matches) > 20):  # only keep most recent top matches
        top_recent_matches_server_ids.pop()
        top_recent_matches.pop()

def update_loop():
    while True:
        update_top_live_matches()
        update_top_recent_matches()
        time.sleep(10)  # wait 10 seconds before next update

if __name__ == '__main__':
    background_updater = threading.Thread(target=update_loop)
    background_updater.daemon = True
    background_updater.start()
    app.run()

