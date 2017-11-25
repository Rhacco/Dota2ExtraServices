from utilities import log
import top_live_matches
import top_recent_matches

from flask import Flask, jsonify
from werkzeug.contrib.fixers import ProxyFix
import threading
import time

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)  # logs visitors' IPs through proxy

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

def update_loop():
    while True:
        top_recent_matches.update()
        top_live_matches.update()
        time.sleep(10)  # wait 10 seconds before next update

if __name__ == '__main__':
    log('Initializing')
    background_updater = threading.Thread(target=update_loop)
    background_updater.daemon = True
    background_updater.start()
    app.run(port=6074)
