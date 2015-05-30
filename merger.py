#!/usr/bin/env python

import argparse
import csv
import json
import sys

parser = argparse.ArgumentParser()
parser.add_argument('ids_file')
parser.add_argument('csv_file')
parser.add_argument('lumisection_data_json')
parser.add_argument('output_csv_file')
args = parser.parse_args()

ids_file = open(args.ids_file)
csv_input = csv.reader(open(args.csv_file))
lumisection_json = json.load(open(args.lumisection_data_json))

csv_output = csv.writer(open(args.output_csv_file, 'w'))

def check_inclusion(run, lumisection):
    run_str = str(run)
    lumisection_int = int(lumisection)
    if not lumisection_json.has_key(run_str):
        return 0
    for section in lumisection_json[run_str]:
        if lumisection_int in xrange(section[0], section[1] + 1):
            return 1
    return 0

for _ in xrange(0, 3):
    ids_file.next()

for index, data in enumerate(csv_input):
    row, run, lumisection = ids_file.next().replace('*', ' ').split()
    valid = check_inclusion(run, lumisection)
    csv_output.writerow([int(row), int(run), int(lumisection), int(valid)] + data)
    if index % 100000 == 0:
        sys.stdout.write('.')
        sys.stdout.flush()

print 'Done!'
