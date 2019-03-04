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

panel_diffs = {
    # '0': {'win': 0, 'loss': 0, 'margin': 0},
    '1': {'win': 0, 'loss': 0, 'margin': 0},
    '2': {'win': 0, 'loss': 0, 'margin': 0},
    '3': {'win': 0, 'loss': 0, 'margin': 0},
    '4': {'win': 0, 'loss': 0, 'margin': 0},
    '5': {'win': 0, 'loss': 0, 'margin': 0},
    '6': {'win': 0, 'loss': 0, 'margin': 0},
}

num_ties = 0
for match in complete_matches:
    if match['winning_alliance'] == '' or match['score_breakdown'] is None:
        continue

    if '--elims' in sys.argv and match['comp_level'] == 'qm':
        continue

    if '--quals' in sys.argv and match['comp_level'] != 'qm':
        continue

    winner = match['winning_alliance']
    loser = 'blue' if match['winning_alliance'] == 'red' else 'red'

    panels = {'red': 0, 'blue': 0}
    for alliance in ['red', 'blue']:
        for bay in [1, 2, 3, 6, 7, 8]:
            panels[alliance] += 1 if match['score_breakdown'][alliance]['preMatchBay' + str(bay)] == 'Panel' else 0

    # winning alliance - losing alliance
    diff = panels[winner] - panels[loser]

    if diff > 0:
        # winning alliance has more panels
        panel_diffs[str(diff)]['win'] += 1
        panel_diffs[str(diff)]['margin'] += match['alliances'][winner]['score'] - match['alliances'][loser]['score']
    elif diff < 0:
        # losing alliance has more panels
        panel_diffs[str(abs(diff))]['loss'] += 1
        panel_diffs[str(abs(diff))]['margin'] += match['alliances'][loser]['score'] - match['alliances'][winner]['score']
    else:
        num_ties += 1

print('Total matches: {}\n'.format(len(complete_matches)))
print('| null panels loaded diff | win ratio | score diff | instances |')
print('| --- | --- | --- | --- |')
for num in panel_diffs:
    total_matches = panel_diffs[num]['win'] + panel_diffs[num]['loss']

    win_ratio = 0
    score_diff = 0

    if total_matches > 0:
        win_ratio = round(panel_diffs[num]['win'] / total_matches, 3)
        score_diff = round(panel_diffs[num]['margin'] / total_matches, 3)

    print('| {} | {} | {} | {} |'.format(num, win_ratio, score_diff, total_matches))
