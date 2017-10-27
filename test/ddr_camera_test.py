import boto3
import datetime
import yaml
from time import sleep
import traceback
import sys

from ddr_server import ddb_util

images_table = 'ddr_images'

s3 = boto3.client('s3')

file_name = sys.argv[1]
#file_name = "image2017-09-22T15_50_50.678439.jpg"
file_ts = file_name[len('image'): len(file_name) - 4].replace('_', ':')
ddb_util.put_files(file_ts)
