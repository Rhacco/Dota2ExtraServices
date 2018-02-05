import json

data = []

def update():
    dotaconstants = 'node_modules/dotaconstants/build/'
    heroes = json.load(open(dotaconstants + 'heroes.json'))
    data_by_hero_name = {}
    for _, hero in heroes.items():
        hero['abilities'] = []
        hero['talents'] = []
        data.append(hero)
        data_by_hero_name[hero['name']] = hero
    hero_abilities = json.load(open(dotaconstants + 'hero_abilities.json'))
    abilities = json.load(open(dotaconstants + 'abilities.json'))
    for hero_name, values in hero_abilities.items():
        for ability_key in values['abilities']:
            if 'hidden' not in ability_key and 'empty' not in ability_key:
                data_by_hero_name[hero_name]['abilities'].append(
                        abilities[ability_key])
        if hero_name == 'npc_dota_hero_invoker':
            for talent in values['talents']:
                if talent['name'].startswith('invoker_'):
                    data_by_hero_name[hero_name]['abilities'].append(
                            abilities[talent['name']])
                else:
                    data_by_hero_name[hero_name]['talents'].append(
                            abilities[talent['name']]['dname'])
        else:
            for talent in values['talents']:
                if 'dname' in abilities[talent['name']]:
                    data_by_hero_name[hero_name]['talents'].append(
                            abilities[talent['name']]['dname'])
