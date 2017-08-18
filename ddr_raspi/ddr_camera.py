#!/usr/bin/env python

# This code is simply for demo and needs to be replaced

from picamera import PiCamera
from time import sleep

import boto3
import yaml
import datetime
images_table = 'ddr_images'

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

def put_item(file_ts):
    table = dynamodb.Table(images_table)
    response = table.put_item(
        Item={
            'file_id': 'DUMMY',
            'file_ts': file_ts, #datetime.datetime.now().isoformat(),
            'file_name': 'image' + file_ts + '.jpg'
        }
    )


with open("ddr_camera.props", 'r') as propsfile:
    props = yaml.load(propsfile)

bucket = props.get('s3_bucket')
rotation = props.get('rotation', 0)
captures_per_second = props.get('captures_per_second', 10)

camera = PiCamera()
camera.rotation = rotation

camera.start_preview()

# camera warmup
sleep(2)

print('camera started')

for i in range(5):
    file_ts = datetime.datetime.now().isoformat()
    filename='image' + file_ts + '.jpg'
    put_item(file_ts)
    pathname='/home/pi/images/' + filename
    camera.capture(pathname)
    sleep(1/captures_per_second)
    data = open(pathname, 'rb')
    s3.upload_file(pathname, bucket, 'images/' + filename)

camera.stop_preview()
print('camera stopped')
