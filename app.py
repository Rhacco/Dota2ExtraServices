from utilities import log
import heroes
import items
import pro_players
import top_live_matches
import top_recent_matches

from flask import Flask, jsonify
from werkzeug.contrib.fixers import ProxyFix
import threading
import time

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)  # logs visitors' IPs through proxy
lock = threading.Lock()

@app.route('/', methods=['GET'])
def get_index():
    return ('Additional Dota 2 services not directly available in the Steam Web'
            ' API. See https://github.com/Rhacco/Dota2ExtraServices')

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

def fetch_new_matches():
    while True:
        lock.acquire()
        top_live_matches.fetch_new_matches()
        lock.release()
        pro_players.update()  # don't create a new thread for this, do it here

def update_registered_matches():
    while True:
        lock.acquire()
        top_recent_matches.handle_finished_matches()
        top_live_matches.update_realtime_stats()
        top_recent_matches.fetch_finished_matches()
        lock.release()

if __name__ == '__main__':
    log('Initializing')
    heroes.fetch()
    items.fetch()
    pro_players.update()
    background_updater1 = threading.Thread(target=fetch_new_matches)
    background_updater1.daemon = True
    background_updater1.start()
    background_updater2 = threading.Thread(target=update_registered_matches)
    background_updater2.daemon = True
    background_updater2.start()
    app.run(port=6074)
