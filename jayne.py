import argparse
import config
from analyze import get_distance
from parse_tei import process_tei
from multiprocessing import Pool
from itertools import combinations
import os
import time
from common import logger, update_status, mkdirp

version = '0.64'

min_length = config.analysis['min_length']
cutoff_score = config.analysis['cutoff_score']
analysis_type = config.analysis["analysis_type"]
process_count = config.system["process_count"]

completed_list = []


# def update_db(job_id, file1, file2, text1, text2, score, score_type):


# This function makes me feel sad
def compare(file1, file2, list1, list2):
    pool = Pool()
    start_time = time.process_time()
    
    data_list = []
    
    results_final = []
    
    for item1 in list1:
        for item2 in list2:
            data_list.append((item1, item2, file1, file2))
    results = pool.starmap(run_comparison, data_list)
    end_time = time.process_time()
    logger('END TIME: {0}'.format(time.strftime("%Y-%m-%d %H:%M:%S")))
    logger('Time to process: '.format(end_time-start_time))
    for result in results:
        if result:
            results_final.append(result)
    return results_final


def generate_pairlist(results):
    keylist = []
    combo_list = []
    for k, v in results.items():
        keylist.append(k)
    combos = combinations(keylist, 2)
    for combo in combos:
        combo_list.append(combo)
    return combo_list


def create_pairs(results):
    pairlist = generate_pairlist(results)
    pairs = []
    for pair in pairlist:
        dict = {
                'file1': pair[0],
                'file2': pair[1],
                'list1': results[pair[0]],
                'list2': results[pair[1]]
                }
        pairs.append(dict)
    return pairs

    
def run_comparison(item1, item2, file1, file2):
    score = get_distance(item1, item2)

    if score <= cutoff_score:
        entry = {'file1': os.path.basename(file1[:-4]),
                 'file2': os.path.basename(file2[:-4]),
                 'text1': item1,
                 'text2': item2,
                 'score': score}
        return entry


def run(in_dir):
    results = process_tei(in_dir, min_length)

    logger("Creating pairs...")

    paired_papers = create_pairs(results)

    logger("Done! Running comparisons.")

    logger('jayne v{0} initialized'.format(version))
    logger('START TIME: {0}'.format(time.strftime("%Y-%m-%d %H:%M:%S")))
    logger('Total number of comparisons requested: '.format(len(paired_papers)))
    logger('Number of independent processes: '.format(process_count))

    comparisons = []

    for pair in paired_papers:
        comparison = compare(pair['file1'], pair['file2'], pair['list1'], pair['list2'])
        comparisons = comparisons + comparison
    return comparisons