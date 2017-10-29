#! /usr/bin/python
import json
import os, fnmatch
import sys, getopt

import yaml

def get_config(key):
    with open("ddr_config.props", 'r') as propsfile:
        props = yaml.load(propsfile)
    return props.get(key)

def listFiles(inputDir, file_ext):
    return fnmatch.filter(os.listdir(inputDir), '*.' + file_ext)

s3bucket = get_config('s3_bucket')
s3_webapp_bucket = get_config('s3_webapp_bucket')
api_url = get_config('api_url')
app_dir = 'scoreboard-web-app'

html_files = listFiles(app_dir, 'html')
js_files = listFiles(app_dir, 'js')

all_files = html_files + js_files

for src_file in all_files:
    print(src_file)
    with open(app_dir + '/' + src_file, 'r+') as f:
        content = f.read()
        f.seek(0)
        f.truncate()
        f.write(content.replace('S3_BUCKET_TOKEN', s3bucket).replace('API_URL_TOKEN', api_url))

