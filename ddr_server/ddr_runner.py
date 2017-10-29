import time
import os
import subprocess
import sys
import traceback
import json

from ddr_server import ddb_util
from ddr_server import ddr_score


def initialize_last_key():
    # The while loop is for the case where raspberry pi has not put any images in S3 yet,
    # hence the dynamodb table storing file names is empty
    lek = {}
    while not lek:
        try:
            r1 = ddb_util.get_first_last_file(False)
            lek = r1['lastEvaluatedKey']
        except:
            time.sleep(0.1)
            lek = {}
    return lek


def calc_conf_mult(rek_arr):
    """Take average of confidence array expressed as a fraction and add 1. Used as score multiplier"""
    rek_mult = 1.0
    if (len(rek_arr)) > 0:
        rek_mult += 0.01 * float(sum(rek_arr))/len(rek_arr)
    return rek_mult


def calc_rek_mult(rek_response):
    """Calculate a single value multiplier from a rekognition response
        (array of smile and happy emotion confidence values)"""
    rek_json = json.loads(rek_response)
    smiles = list(map(lambda e: float(e['Confidence']), [y for y in rek_json['Smiles'] if y['Value']]))
    emotions = list(map(lambda e: float(e['Confidence']), [y for sublist in rek_json['Emotions'] for y in sublist if y['Type'] == 'HAPPY']))
    smiles_mult = calc_conf_mult(smiles)
    emotions_mult = calc_conf_mult(emotions)
    return emotions_mult * smiles_mult


def openpose_process():
    previous_run_files = []
    while True:
        try:
            r = ddb_util.get_two_latest_files()
            this_run_files = r['files']
            if (len(this_run_files) is 2) and (sorted(this_run_files) != sorted(previous_run_files)):
                # print("Starting sub process ")
                # subprocess.call(os.path.expanduser('~') + '/' + 'openpose.sh')
                file1 = os.path.expanduser('~') + '/json/' + 'image' + str(this_run_files[0]).replace(':','_') + '.json'
                file2 = os.path.expanduser('~') + '/json/' + 'image' + str(this_run_files[1]).replace(':','_') + '.json'

                if os.path.isfile(file1) and os.path.isfile(file2):
                    group_score = ddr_score.fetch_score(file1, file2)
                    rek_responses = r['rek_responses']
                    rek_multiples = list(map(calc_rek_mult, rek_responses))
                    avg_rek_multiple = sum(rek_multiples) / float(len(rek_multiples))
                    max_rek_multiple = max(rek_multiples)
                    group_score.append(avg_rek_multiple)
                    group_score.append(max_rek_multiple)
                    ddb_util.put_score(group_score)
                else:
                    print("Error: did not find json files: " + str(this_run_files))

                previous_run_files = this_run_files

            else:
                print("No new file, sleeping 1 seconds")
                time.sleep(1)
                continue

            print(this_run_files)

        except:
            print("Error occurred in main server loop")
            traceback.print_exc()
            time.sleep(1)


def main(argv):
    ddb_util.setup_ddb_tables()
    openpose_process()


if __name__ == '__main__':
    main(sys.argv[1:])
