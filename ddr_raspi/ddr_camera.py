#!/usr/bin/env python

# This code is simply for demo and needs to be replaced

import boto3
import datetime
import yaml
from picamera import PiCamera
from time import sleep
import traceback

from ddr_server import ddb_util

images_table = 'ddr_images'

s3 = boto3.client('s3')

with open("ddr_camera.props", 'r') as propsfile:
    props = yaml.load(propsfile)

bucket = props.get('s3_bucket')
rotation = props.get('rotation', 0)
captures_per_second = props.get('captures_per_second', 10)

camera = PiCamera()
camera.rotation = rotation
camera.resolution = (800, 600)
camera.start_preview(alpha=128)

# camera warmup
sleep(2)

print('camera started')

while True:
    try:
        file_ts = datetime.datetime.now().isoformat()
        file_ts_enc = file_ts.replace(':','_')
        filename='image' + file_ts_enc + '.jpg'
        ddb_util.put_files(file_ts)
        pathname='/home/pi/images/' + filename
        camera.capture(pathname)
        sleep(1/captures_per_second)
        data = open(pathname, 'rb')
        s3.upload_file(pathname, bucket, 'images/' + filename)
    except:
        traceback.print_exc()


#Infinite loop so the close below is no longer reachable.
# Python process on raspberry pi needs to be killed to stop capture
#camera.stop_preview()
#print('camera stopped')
