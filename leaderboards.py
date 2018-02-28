from utilities import log
import api

import time
import datetime

data = {}
regions = ['americas', 'europe', 'se_asia', 'china']
last_update = 0
_top_100_entries = {'americas': {}, 'europe': {}, 'se_asia': {}, 'china': {}}
_expiration_date = datetime.datetime.now()
_is_first_update = True

def update():
    global last_update
    global _expiration_date
    global _is_first_update
    now = datetime.datetime.now()
    if now > _expiration_date:
        for region in regions:
            dota2_leaderboard = []
            try:
                dota2_leaderboard = api.dota2_get_leaderboard(region)
            except:
                continue
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
                last_rank = 0
                if new_entry['name'] in _top_100_entries[region]:
                    old_entry = _top_100_entries[region][new_entry['name']]
                    last_rank = old_entry['rank']
                if new_entry['rank'] <= 100:
                    name = new_entry['name']
                    if name and not name.isspace():      # ignore empty names
                        if not name == len(name) * '.':  # and only dots
                            _top_100_entries[region][name] = new_entry
                            if last_rank > 0:
                                new_entry['last_rank'] = last_rank
                            elif not _is_first_update:
                                new_entry['new_in_top_100'] = True
                elif new_entry['name'] in _top_100_entries[region]:
                    _top_100_entries[region].pop(new_entry['name'])
                new_leaderboard.append(new_entry)
            data[region] = new_leaderboard
        last_update = time.time()
        _expiration_date = _expiration_date + datetime.timedelta(hours=1)
        _is_first_update = False
