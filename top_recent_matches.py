import api
import top_live_matches

server_ids = []
data = []

def update():
    to_remove = []
    index = 0
    while index < len(top_live_matches.data):
        try:
            # If this succeeds, match details are present and match is finished
            finished_top_match = api.dota2.get_match_details(
                    top_live_matches.match_ids[index])
            server_ids.insert(0, top_live_matches.server_ids[index])
            data.insert(0, finished_top_match)
            to_remove.append(index)
        except:
            pass
        index += 1
    index = 0
    while index < len(to_remove):
        top_live_matches.remove(to_remove[index] - index)
        index += 1
    while (len(data) > 20):  # only keep most recent top matches
        server_ids.pop()
        data.pop()

#def __convert(finished_top_match):
    # TODO