from utilities import log
import heroes
import items
import pro_players
import top_live_matches
import top_recent_matches
import leaderboards

from flask import Flask, jsonify, request
import threading

app = Flask(__name__)


@app.route('/', methods=['GET'])
def get_index():
    return ('Additional Dota 2 services not directly available in the Steam '
            'Web API. See https://github.com/Rhacco/Dota2ExtraServices')


@app.route('/Heroes', methods=['GET'])
def get_heroes():
    return jsonify(heroes.data)


@app.route('/Items', methods=['GET'])
def get_items():
    return jsonify(items.data)


@app.route('/TopLiveMatches', methods=['GET'])
def get_top_live_matches():
    return jsonify(top_live_matches.data)


@app.route('/TopRecentMatches', methods=['GET'])
def get_top_recent_matches():
    return jsonify(list(top_recent_matches.data.values()))


@app.route('/Leaderboard', methods=['GET'])
def get_leaderboard():
    region = request.args.get('region')
    if region is not None:
        if region in leaderboards.data:
            return jsonify(leaderboards.data[region])
        else:
            return ('Parameter \'region\' is invalid, must be either '
                    '\'americas\', \'europe\', \'se_asia\' or \'china\'.')
    else:
        return ('Required parameter \'region\' is missing, must be either '
                '\'americas\', \'europe\', \'se_asia\' or \'china\'.')


@app.route('/LastUpdates', methods=['GET'])
def get_last_updates():
    return jsonify({
        'heroes': heroes.last_update,
        'items': items.last_update,
        'leaderboards': leaderboards.last_update
    })


def update_loop():
    while True:
        pro_players.update()
        leaderboards.update()
        top_live_matches.fetch_new_matches()
        top_recent_matches.handle_finished_matches()
        top_live_matches.update_realtime_stats()
        top_recent_matches.fetch_finished_matches()


if __name__ == '__main__':
    log('Initializing')
    heroes.update()
    items.update()
    background_updater = threading.Thread(target=update_loop)
    background_updater.daemon = True
    background_updater.start()
    app.run(port=6074)
