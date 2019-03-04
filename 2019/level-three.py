# This program analyzes the effect of preloading null hatch panels
# on the outcome of a match, including the win percentage and average
# score difference.

import json
import os
import sys

import tbapy

with open('../key.txt') as keyfile:
    key = keyfile.read().strip()

file = '../matches.json'

tba = tbapy.TBA(key)

weeks = [0]
events = filter(lambda e: e['week'] in weeks, tba.events(2019))

complete_matches = []

# Load matches from TBA or from file if already loaded
if not os.path.isfile(file):
    for event in events:
        matches = tba.event_matches(event['key'])

        print('Gathered {} matches from {}'.format(len(matches), event['key']))

        for match in matches:
            if match['actual_time'] is not None:
                complete_matches.append(match)

    with open(file, 'w') as outfile:
        json.dump(complete_matches, outfile)
else:
    with open(file, 'r') as infile:
        complete_matches = json.load(infile)

levels = { }

for match in complete_matches:
    if match['winning_alliance'] == '' or match['score_breakdown'] is None:
        continue

    if '--elims' in sys.argv and match['comp_level'] == 'qm':
        continue

    if '--quals' in sys.argv and match['comp_level'] != 'qm':
        continue

    for alliance in ['red', 'blue']:
        climb_level_1 = 0
        climb_level_2 = 0
        climb_level_3 = 0

        for robot in [1, 2, 3]:
            if match['score_breakdown'][alliance]['endgameRobot' + str(robot)] == 'HabLevel1':
                climb_level_1 += 1

            if match['score_breakdown'][alliance]['endgameRobot' + str(robot)] == 'HabLevel2':
                climb_level_2 += 1

            if match['score_breakdown'][alliance]['endgameRobot' + str(robot)] == 'HabLevel3':
                climb_level_3 += 1

        total_climb = climb_level_1 + climb_level_2 + climb_level_3
        level = '{}-{}-{}-{}'.format(3 - total_climb, climb_level_1, climb_level_2, climb_level_3)

        if level not in levels:
            levels[level] = {
                'win': 1 if match['winning_alliance'] == alliance else 0,
                'loss': 0 if match['winning_alliance'] == alliance else 1,
                'margin': match['alliances'][alliance]['score']
            }
        else:
            levels[level]['win' if match['winning_alliance'] == alliance else 'loss'] += 1
            levels[level]['margin'] += match['alliances'][alliance]['score']

to_print = []
for num in levels:
    total_matches = levels[num]['win'] + levels[num]['loss']
    win_ratio = round(levels[num]['win'] / total_matches, 3)
    score_diff = round(levels[num]['margin'] / total_matches, 3)

    to_print.append((num, win_ratio, score_diff, total_matches))

to_print = sorted(to_print, key=lambda a: a[1], reverse=True)

print('Total matches: {}\n'.format(len(complete_matches)))
print('| climb levels | win ratio | avg score | instances |')
print('| --- | --- | --- | --- |')
for num, win_ratio, score_diff, total_matches in to_print:
    print('| {} | {} | {} | {} |'.format(num, win_ratio, score_diff, total_matches))
