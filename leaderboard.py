#!/usr/bin/env python3

from scipy.stats import spearmanr
import sys
import json
import csv


class LeaderBoard:
    def __init__(self, data_line):
        self.data = json.loads(data_line)
        self.users_bot_flags = {}
        for d in self.data:
            if d['evaluation'][0]['userId'] == 'Alice':
                self.users_bot_flags[d['dialogId']] = (int(d['evaluation'][0]['quality']),
                                                       int(d['evaluation'][1]['quality']))
            else:
                self.users_bot_flags[d['dialogId']] = (int(d['evaluation'][1]['quality']),
                                                       int(d['evaluation'][0]['quality']))

    def score(self, csv_lines):
        users_bot_fact_labels = []
        users_bot_predicted_probs = []

        used_dialogs = set()

        submission_reader = csv.reader(csv_lines, delimiter=',', quotechar='|')
        for row in submission_reader:
            try:
                dialog = int(row[0])
                alice = float(row[1])
                bob = float(row[2])
            except (ValueError, IndexError):
                continue

            if dialog in self.users_bot_flags and dialog not in used_dialogs:
                users_bot_fact_labels.append(self.users_bot_flags[dialog][0])
                users_bot_predicted_probs.append(alice)

                users_bot_fact_labels.append(self.users_bot_flags[dialog][1])
                users_bot_predicted_probs.append(bob)

                used_dialogs.add(dialog)
            else:
                print("dialog %s not in dataset" % dialog, file=sys.stderr)

        if len(self.users_bot_flags) == len(users_bot_fact_labels) // 2 == len(users_bot_predicted_probs) // 2:
            return True, str(spearmanr(users_bot_fact_labels, users_bot_predicted_probs).correlation)
        else:
            return False, "You haven't scored all the dialogs."


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("example: leaderboard.py <labels.csv> [<data.json>]", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) == 2:
        lines = sys.stdin.readlines()
        line = "[" + ",".join(lines) + "]"
    else:
        with open(sys.argv[2]) as f:
            line = f.read()

    lb = LeaderBoard(line)

    with open(sys.argv[1], 'rt') as csv_file:
        scoring = lb.score(csv_file)

    if scoring[0]:
        print(sys.argv[1], ": ", scoring[1])
    else:
        print(scoring[1], file=sys.stderr)


if __name__ == "__main__":
    main()
