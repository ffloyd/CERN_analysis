#!/usr/bin/env python

import numpy as np
import itertools
from sets import Set
import csv
import argparse
import logging

parser = argparse.ArgumentParser()
parser.add_argument('csv_files', nargs='+')
parser.add_argument('good_csv_out')
parser.add_argument('bad_csv_out')
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
logging.info('Start processing...')

def get_stats_from_file(input_csv):
    logging.info('Loading file ' + input_csv + '...')
    dtypes = {
        'names': ('row', 'run', 'lumisection', 'valid',
                  'data1', 'data2', 'data3', 'data4', 'data5', 'data6', 'data7'),
        'formats': (np.int, np.int, np.int, np.int,
                    np.double, np.double, np.double, np.double, np.double, np.double, np.double)
    }
    data = np.loadtxt(input_csv, delimiter=',', dtype=dtypes)

    logging.info('Determining valid and invalid (run, lumisection) pairs...')

    valid_blocks_params = Set()
    invalid_blocks_params = Set()

    for row in np.nditer(data):
        params = (row['run'].item(), row['lumisection'].item())
        if row['valid'] == 1:
            valid_blocks_params.add(params)
        else:
            invalid_blocks_params.add(params)

    def get_stats(run, lumisection, col):
        block = data[(data['run'] == run) & (data['lumisection'] == lumisection)]
        median = np.median(block[col])
        mean = np.mean(block[col])
        std = np.std(block[col])
        return median, mean, std

    def get_all_stats_by_param(param):
        run, lumisection = param
        cols = ['data' + str(x) for x in xrange(1, 8)]
        result = [(run, lumisection)] + [get_stats(run, lumisection, x) for x in cols]
        return list(itertools.chain(*result))

    logging.info('Collect valid blocks stats...')
    valid_blocks_stats = [get_all_stats_by_param(x) for x in valid_blocks_params]
    logging.info('Collect invalid blocks stats...')
    invalid_blocks_stats = [get_all_stats_by_param(x) for x in invalid_blocks_params]

    logging.info(input_csv + ' is processed.')

    return valid_blocks_stats, invalid_blocks_stats

good_data, bad_data = [], []

for filename in args.csv_files:
    new_good_data, new_bad_data = get_stats_from_file(filename)
    good_data.append(new_good_data)
    bad_data.append(new_bad_data)

logging.info('Combine data together...')
all_good_data = itertools.chain(*good_data)
all_bad_data = itertools.chain(*bad_data)

good_csv = csv.writer(open(args.good_csv_out, 'w'))
bad_csv = csv.writer(open(args.bad_csv_out, 'w'))

logging.info('Write valid blocks data...')
good_csv.writerows(all_good_data)

logging.info('Write invalid blocks data...')
bad_csv.writerows(all_bad_data)
