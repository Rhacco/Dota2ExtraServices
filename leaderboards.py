from utilities import log
import api

import datetime

data = {}
regions = ['americas', 'europe', 'se_asia', 'china']
__entries = {'americas': {}, 'europe': {}, 'se_asia': {}, 'china': {}}
__expiration_date = datetime.datetime.now()

def update():
    global __expiration_date
    now = datetime.datetime.now()
    if now > __expiration_date:
        for region in regions:
            dota2_leaderboard = []
            try:
                dota2_leaderboard = api.dota2_get_leaderboard(region)
            except Exception as e:
                log('Failed to update a leaderboard: ' + str(e))
                return
            new_leaderboard = []
            for index, entry in enumerate(dota2_leaderboard):
                new_entry = {}
                new_entry['rank'] = index + 1
                try:
                    team_tag = entry['team_tag'] 
                    if team_tag:
                        new_entry['name'] = team_tag + '.' + entry['name']
                    else:
                        new_entry['name'] = entry['name']
                except:
                    new_entry['name'] = entry['name']
                if new_entry['name'] in __entries[region]:
                    old_entry = __entries[region][new_entry['name']]
                    if new_entry['rank'] > old_entry['rank']:
                        new_entry['rank_change'] = 'up'
                    elif new_entry['rank'] < old_entry['rank']:
                        new_entry['rank_change'] = 'down'
                    else:
                        new_entry['rank_change'] = 'same'
                else:
                    new_entry['rank_change'] = 'same'
                new_leaderboard.append(new_entry)
                __entries[region][new_entry['name']] = new_entry
            data[region] = new_leaderboard
        __expiration_date = now + datetime.timedelta(days=1)
        log('Updated leaderboards')
