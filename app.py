from utilities import log
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

@app.route('/TopLiveMatches', methods=['GET'])
def get_top_live_matches():
    return jsonify(top_live_matches.data)

@app.route('/TopRecentMatches', methods=['GET'])
def get_top_recent_matches():
    return jsonify(top_recent_matches.data)

def fetch_new_matches():
    while True:
        lock.acquire()
        top_live_matches.fetch_new_matches()
        lock.release()
        time.sleep(1)  # only wait 1 second to not miss any matches

def update_registered_matches():
    while True:
        lock.acquire()
        top_recent_matches.handle_finished_matches()
        top_live_matches.update_realtime_stats()
        lock.release()
        # don't wait at all here since the API calls take long enough

if __name__ == '__main__':
    log('Initializing')
    background_updater1 = threading.Thread(target=fetch_new_matches)
    background_updater1.daemon = True
    background_updater1.start()
    background_updater2 = threading.Thread(target=update_registered_matches)
    background_updater2.daemon = True
    background_updater2.start()
    app.run(port=6074)
