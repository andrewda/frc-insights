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

        for match in matches:
            if match['actual_time'] is not None:
                complete_matches.append(match)

    with open(file, 'w') as outfile:
        json.dump(complete_matches, outfile)
else:
    with open(file, 'r') as infile:
        complete_matches = json.load(infile)

panels = {
    '0': {'win': 0, 'loss': 0, 'margin': 0},
    '1': {'win': 0, 'loss': 0, 'margin': 0},
    '2': {'win': 0, 'loss': 0, 'margin': 0},
    '3': {'win': 0, 'loss': 0, 'margin': 0},
    '4': {'win': 0, 'loss': 0, 'margin': 0},
    '5': {'win': 0, 'loss': 0, 'margin': 0},
    '6': {'win': 0, 'loss': 0, 'margin': 0},
}

for match in complete_matches:
    if match['winning_alliance'] == '' or match['score_breakdown'] is None:
        continue

    if '--elims' in sys.argv and match['comp_level'] == 'qm':
        continue

    if '--quals' in sys.argv and match['comp_level'] != 'qm':
        continue

    for alliance in ['red', 'blue']:
        null_panels = 0
        for bay in [1, 2, 3, 6, 7, 8]:
            null_panels += 1 if match['score_breakdown'][alliance]['preMatchBay' + str(bay)] == 'Panel' else 0

        panels[str(null_panels)]['win' if match['winning_alliance'] == alliance else 'loss'] += 1
        panels[str(null_panels)]['margin'] += match['alliances'][alliance]['score'] - match['alliances']['blue' if alliance == 'red' else 'red']['score']

print('Total matches: {}\n'.format(len(complete_matches)))
print('| null panels loaded | win ratio | score diff | instances |')
print('| --- | --- | --- | --- |')
for num in panels:
    total_matches = panels[num]['win'] + panels[num]['loss']

    win_ratio = 0
    score_diff = 0

    if total_matches > 0:
        win_ratio = round(panels[num]['win'] / total_matches, 3)
        score_diff = round(panels[num]['margin'] / total_matches, 3)

    print('| {} | {} | {} | {} |'.format(num, win_ratio, score_diff, total_matches))
