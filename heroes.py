import json
from utilities import list_to_string
from utilities import make_camel_case

data = []

def update():
    dotaconstants = 'node_modules/dotaconstants/build/'
    heroes = json.load(open(dotaconstants + 'heroes.json'))
    data_by_hero_name = {}
    for _, hero in heroes.items():
        hero['abilities'] = []
        hero['talents'] = []
        _insert_sorted(hero)
        data_by_hero_name[hero['name']] = hero
    hero_abilities = json.load(open(dotaconstants + 'hero_abilities.json'))
    abilities = json.load(open(dotaconstants + 'abilities.json'))
    for hero_name, values in hero_abilities.items():
        for ability_key in values['abilities']:
            if 'hidden' not in ability_key and 'empty' not in ability_key:
                data_by_hero_name[hero_name]['abilities'].append(
                        _convert(abilities[ability_key]))
        if hero_name == 'npc_dota_hero_invoker':
            for talent in values['talents']:
                if talent['name'].startswith('invoker_'):
                    data_by_hero_name[hero_name]['abilities'].append(
                        _convert(abilities[talent['name']]))
                else:
                    data_by_hero_name[hero_name]['talents'].append(
                            abilities[talent['name']]['dname'])
        else:
            for talent in values['talents']:
                if 'dname' in abilities[talent['name']]:
                    data_by_hero_name[hero_name]['talents'].append(
                            abilities[talent['name']]['dname'])

def _convert(ability):
    # Convert some lists of strings to only one string and capitalize CamelCase
    if isinstance(ability['behavior'], list):
        ability['behavior'] = list_to_string(ability['behavior'], ', ')
    for attrib in ability['attrib']:
        converted = make_camel_case(attrib['header'].replace('\\n', ''))
        attrib['header'] = converted.replace(' Hp ', ' HP ')
        if isinstance(attrib['value'], list):
            attrib['value'] = list_to_string(attrib['value'], ' / ')
    if 'cd' in ability and isinstance(ability['cd'], list):
        ability['cd'] = list_to_string(ability['cd'], ' / ')
    if 'mc' in ability and isinstance(ability['mc'], list):
        ability['mc'] = list_to_string(ability['mc'], ' / ')
    return ability

def _insert_sorted(new_hero):
    for index, hero in enumerate(data):
        if new_hero['localized_name'] < hero['localized_name']:
            data.insert(index, new_hero)
            return
    data.append(new_hero)
