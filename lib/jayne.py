import argparse
import config
from lib.analyze import get_distance
from lib.parse_tei import process_tei
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from itertools import combinations
import os
import time
from lib.common import logger, update_status, mkdirp
from lib.preprocess import preprocess

"""
Main functions cribbed from https://github.com/seanrife/jayne
Compares sets of strings and returns ones above a set level
of similarity.
"""

version = '0.64'

min_length = config.analysis['min_length']
cutoff_score = config.analysis['cutoff_score']
analysis_type = config.analysis["analysis_type"]
process_count = config.system["process_count"]

completed_list = []


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


# This function makes me feel sad
def compare(file1, file2, list1, list2, cutoff_score):
    logger(f"Comparing {file1} and {file2}.")
    pool = Pool(processes=process_count)
    
    data_list = []
    
    results_final = []
    
    preprocessed_results = preprocess(list1, list2)
    
    preprocessed_results = sorted(preprocessed_results, key=lambda d: d['score'], reverse=True)
            
    for row in preprocessed_results:
        data_list.append((row['item1'], row['item2'], file1, file2, cutoff_score))
        
    data_list_chunked = divide_chunks(data_list, 10)
    
    for chunk in data_list_chunked:
        results = pool.starmap(run_comparison, chunk)
        print(results)
        for result in results:
            if result:
                results_final.append(result)
            else:
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

    
def run_comparison(item1, item2, file1, file2, cutoff_score):
    score = get_distance(item1, item2)

    if score <= cutoff_score:
        entry = {'file1': os.path.basename(file1[:-4]),
                 'file2': os.path.basename(file2[:-4]),
                 'text1': item1,
                 'text2': item2,
                 'score': score}
        return entry


def run(in_dir, cutoff_score):
    thread_pool = ThreadPool(96)
    results = process_tei(in_dir, min_length)

    logger("Creating pairs...")

    paired_papers = create_pairs(results)


    logger("Done! Running comparisons.")

    logger('jayne v{0} initialized'.format(version))
    logger('Total number of comparisons requested: {0}'.format(len(paired_papers)))
    logger('Number of independent processes: {0}'.format(process_count))

    comparisons = []

    for pair in paired_papers:
        comparison = thread_pool.starmap(compare, [(pair['file1'], pair['file2'], pair['list1'], pair['list2'], cutoff_score)])
        comparisons = comparisons + comparison
    return comparisons
