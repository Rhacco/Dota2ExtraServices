from utilities import log
import api

import datetime

data = {}
__expiration_date = datetime.datetime.now()

def update():
    global __expiration_date
    now = datetime.datetime.now()
    if now > __expiration_date:
        opendota_pro_players = []
        try:
            opendota_pro_players = api.opendota_get_pro_players()
        except Exception as e:
            log('Failed to update pro players: ' + str(e))
            return
        data.clear()
        for pro_player in opendota_pro_players:
            data[int(pro_player['account_id'])] = pro_player
        __expiration_date = now + datetime.timedelta(hours=8)
        log('Updated pro players')