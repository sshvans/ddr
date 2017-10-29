import boto3
import datetime
import yaml
from time import sleep
import traceback
import sys
import json

from ddr_server import ddb_util


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



res = ddb_util.get_two_latest_files()
print("RES: ")
print(res)
print(res['files'])
rek_responses = res['rek_responses']
rek_multiples = list(map(calc_rek_mult, rek_responses))
avg_rek_multiple = sum(rek_multiples) / float(len(rek_multiples))
max_rek_multiple = max(rek_multiples)
print(avg_rek_multiple)
print(max_rek_multiple)

for x in rek_responses:
    print("Entry: " + x)
    xj = json.loads(x)
    print("Smiles:")
    #y = xj['Smiles']
    for y in xj['Smiles']:
        if y['Value']:
            print(y['Confidence'])
    print("Emotions:")
    #z = [xj['Emotions'] for w in xj['Emotions'] if w['Type'] == 'HAPPY']
    #print(z)
    for w in xj['Emotions']:
        #print(json.loads(w))
        for wi in w:
            if wi['Type'] == 'HAPPY':
                print(wi['Confidence'])

    smiles = list(map(lambda e: float(e['Confidence']), [y for y in xj['Smiles'] if y['Value']]))
    #emotions = list(map(lambda e: e['Confidence'], [y for y in xj['Emotions']]))
    #[item for sublist in l for item in sublist]
    emotions = list(map(lambda e: float(e['Confidence']), [y for sublist in xj['Emotions'] for y in sublist if y['Type'] == 'HAPPY']))

    smiles_mult = calc_conf_mult(smiles)
    emotions_mult = calc_conf_mult(emotions)

    print("SMILES:")
    print(smiles)
    print("EMOTIONS:")
    print(emotions)

    print(smiles_mult)
    print(emotions_mult)

    print(smiles_mult * emotions_mult)
    print(calc_rek_mult(x))


# images_table = 'ddr_images'
#
# s3 = boto3.client('s3')
#
# file_name = sys.argv[1]
# #file_name = "image2017-09-22T15_50_50.678439.jpg"
# file_ts = file_name[len('image'): len(file_name) - 4].replace('_', ':')
# ddb_util.put_files(file_ts)

